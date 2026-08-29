"""
Recoup — Auditor Node.

Writes an immutable, timestamped record to the audit store.
This is the final checkpoint — after this, the case is considered fully processed.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from app.graph.state import RecoveryCase
from app.database import DB_PATH


def auditor_node(state: RecoveryCase) -> dict:
    """
    Auditor node — writes the full case to the immutable audit store.

    This is append-only — we never update or delete audit entries.
    The dashboard reads from this store.
    """
    start_time = datetime.now(timezone.utc)

    case_id = state.get("case_id", "")
    case_status = state.get("case_status", "executed")

    # Determine final status based on execution
    execution_status = state.get("execution_status", "")
    if execution_status == "success":
        # Simulate recovery — in a real system, this would be confirmed by
        # a payment_link.paid webhook or a payment.captured event
        import random
        recovery_chance = 0.65  # 65% simulated recovery rate
        recovered = random.random() < recovery_chance
        if recovered:
            recovery_amount = state.get("amount_at_risk", 0)
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

    return {
        "case_status": final_status,
        "recovery_amount": recovery_amount,
        "updated_at": end_time.isoformat(),
        "audit_trail": [audit_entry],
    }
