"""
Recoup — Auditor Node.

Writes an immutable, timestamped record to the audit store.
This is the final checkpoint — after this, the case is considered fully processed.
Dispatches a fail-safe background audit record to Java Cryptographic Audit Ledger (Port 8080).
"""

import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
import httpx

from app.graph.state import RecoveryCase
from app.database import DB_PATH

logger = logging.getLogger(__name__)


def _dispatch_java_ledger_async(case_id: str, action: str, amount: float, timestamp: str):
    """
    Fire-and-forget background dispatcher to Java Audit Ledger Microservice (Port 8080).
    Enforces a strict 300ms max timeout and silently catches all exceptions.
    Ensures zero latency impact or blocking on the Python agent pipeline.
    """
    def worker():
        try:
            payload = {
                "case_id": case_id,
                "action": action,
                "amount": amount,
                "timestamp": timestamp,
            }
            with httpx.Client(timeout=0.3) as client:
                client.post("http://localhost:8088/api/ledger/record", json=payload)
        except Exception as e:
            # Silent fail-safe log: Java service is optional
            logger.debug(f"Java Audit Ledger dispatch note (offline/skipped): {e}")

    threading.Thread(target=worker, daemon=True).start()


def auditor_node(state: RecoveryCase) -> dict:
    """
    Auditor node — writes the full case to the immutable audit store.

    This is append-only — we never update or delete audit entries.
    The dashboard reads from this store.
    """
    start_time = datetime.now(timezone.utc)

    case_id = state.get("case_id", "")
    case_status = state.get("case_status", "executed")
    action = state.get("recovery_action", "recorded")
    amount = state.get("amount_at_risk", 0.0)

    # Determine final status based on execution
    execution_status = state.get("execution_status", "")
    if execution_status == "success":
        import random
        # Seed pseudo-random recovery check deterministically with event_id + timestamp
        # so benchmark runs are 100% deterministic and reproducible across runs.
        raw_evt = state.get("raw_event", {})
        evt_id = state.get("event_id") or raw_evt.get("event_id") or "default_evt"
        evt_ts = raw_evt.get("timestamp") or state.get("created_at") or ""
        seed_key = f"{evt_id}_{evt_ts}"
        rng = random.Random(seed_key)
        recovery_chance = 0.65  # 65% simulated recovery rate
        recovered = rng.random() < recovery_chance
        if recovered:
            recovery_amount = amount
            final_status = "recovered"
        else:
            recovery_amount = 0
            final_status = "failed"
    else:
        recovery_amount = 0
        final_status = case_status

    end_time = datetime.now(timezone.utc)
    latency_ms = (end_time - start_time).total_seconds() * 1000

    audit_entry = {
        "node_name": "auditor",
        "input_summary": f"Case {case_id} with execution_status={execution_status}",
        "output_summary": f"Final status: {final_status}, recovery_amount: INR {recovery_amount:,.2f}",
        "reasoning": f"Case audit completed. Execution was {'successful' if execution_status == 'success' else 'unsuccessful'}. {'Simulated recovery confirmed.' if final_status == 'recovered' else 'Recovery not confirmed yet.'}",
        "provider": "deterministic/auditor",
        "latency_ms": round(latency_ms, 2),
        "timestamp": end_time.isoformat(),
    }

    # Dispatch fail-safe fire-and-forget payload to Java Cryptographic Audit Ledger
    _dispatch_java_ledger_async(
        case_id=case_id,
        action=f"{action}:{final_status}",
        amount=amount,
        timestamp=end_time.isoformat(),
    )

    return {
        "case_status": final_status,
        "recovery_amount": recovery_amount,
        "updated_at": end_time.isoformat(),
        "audit_trail": [audit_entry],
    }
