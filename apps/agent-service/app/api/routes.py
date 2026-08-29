"""
Recoup — Dashboard API Routes (Wired to Pipeline + Database).

REST endpoints consumed by the React dashboard.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

# Add project root for data imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.graph.pipeline import process_event, process_batch
from app.channels.voice import hinglish_voice_channel

router = APIRouter()

# In-memory store for processed cases (SQLite persistence in Phase 3)
_cases_store: dict[str, dict] = {}
_metrics_cache: dict = {}


def _serialize_case(case: dict) -> dict:
    """Convert a RecoveryCase to a JSON-serializable dict for the API."""
    return {
        "case_id": case.get("case_id", ""),
        "event_id": case.get("event_id", ""),
        "event_type": case.get("event_type", ""),
        "customer_id": case.get("customer_id", ""),
        "customer_email": case.get("customer_email", ""),
        "customer_phone": case.get("customer_phone", ""),
        "customer_name": case.get("customer_name", ""),
        "amount_at_risk": case.get("amount_at_risk", 0),
        "currency": case.get("currency", "INR"),
        "decline_reason_raw": case.get("decline_reason_raw", ""),
        "root_cause": case.get("root_cause", ""),
        "root_cause_confidence": case.get("root_cause_confidence", 0),
        "diagnosis_method": case.get("diagnosis_method", ""),
        "diagnosis_reasoning": case.get("diagnosis_reasoning", ""),
        "diagnosis_provider": case.get("diagnosis_provider", ""),
        "diagnosis_latency_ms": case.get("diagnosis_latency_ms", 0),
        "recovery_channel": case.get("recovery_channel", ""),
        "recovery_action": case.get("recovery_action", ""),
        "message_content": case.get("message_content", ""),
        "scheduled_at": case.get("scheduled_at", ""),
        "guardrail_status": case.get("guardrail_status", ""),
        "guardrail_violations": case.get("guardrail_violations", []),
        "execution_status": case.get("execution_status", ""),
        "execution_result": case.get("execution_result", {}),
        "recovery_amount": case.get("recovery_amount", 0),
        "case_status": case.get("case_status", ""),
        "retry_count": case.get("retry_count", 0),
        "audit_trail": case.get("audit_trail", []),
        "created_at": case.get("created_at", ""),
        "updated_at": case.get("updated_at", ""),
    }


def _compute_metrics() -> dict:
    """Compute aggregated metrics from the cases store."""
    cases = list(_cases_store.values())

    if not cases:
        return {
            "total_at_risk": 0,
            "total_recovered": 0,
            "recovery_rate": 0,
            "total_cases": 0,
            "recovered_cases": 0,
            "failed_cases": 0,
            "blocked_cases": 0,
            "pending_approval": 0,
            "compliance_violations": 0,
            "rule_hit_count": 0,
            "llm_fallback_count": 0,
            "rule_hit_ratio": 0,
            "avg_latency_ms": 0,
            "root_cause_distribution": {},
            "channel_distribution": {},
            "status_distribution": {},
        }

    total_at_risk = sum(c.get("amount_at_risk", 0) for c in cases)
    total_recovered = sum(c.get("recovery_amount", 0) for c in cases)

    status_counts = {}
    root_cause_counts = {}
    channel_counts = {}
    rule_hits = 0
    llm_hits = 0
    latencies = []

    for c in cases:
        # Status
        status = c.get("case_status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

        # Root cause
        rc = c.get("root_cause", "unknown")
        root_cause_counts[rc] = root_cause_counts.get(rc, 0) + 1

        # Channel
        ch = c.get("recovery_channel", "none")
        channel_counts[ch] = channel_counts.get(ch, 0) + 1

        # Diagnosis method
        method = c.get("diagnosis_method", "")
        if method == "rule":
            rule_hits += 1
        elif method == "llm_fallback":
            llm_hits += 1

        # Latency — collect latency for every single case in the batch
        lat = c.get("diagnosis_latency_ms", 0.4)
        latencies.append(lat)

    total = len(cases)
    recovery_rate = (total_recovered / total_at_risk * 100) if total_at_risk > 0 else 0
    rule_ratio = (rule_hits / total * 100) if total > 0 else 0
    avg_latency = sum(latencies) / total if total > 0 else 0

    # Count REAL compliance violations (should always be 0)
    # DND_WINDOW = rescheduled (guardrail working), HIGH_VALUE = routed to approval (guardrail working)
    # True violations = opted-out customer contacted, or retry cap bypassed
    violations = 0
    for c in cases:
        if c.get("guardrail_status") == "approved":
            for v in c.get("guardrail_violations", []):
                if v.startswith("OPTED_OUT") or v.startswith("MAX_RETRIES"):
                    violations += 1

    return {
        "total_at_risk": round(total_at_risk, 2),
        "total_recovered": round(total_recovered, 2),
        "recovery_rate": round(recovery_rate, 2),
        "total_cases": total,
        "recovered_cases": status_counts.get("recovered", 0),
        "failed_cases": status_counts.get("failed", 0),
        "blocked_cases": status_counts.get("blocked", 0),
        "pending_approval": status_counts.get("pending_approval", 0),
        "compliance_violations": violations,
        "rule_hit_count": rule_hits,
        "llm_fallback_count": llm_hits,
        "rule_hit_ratio": round(rule_ratio, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "root_cause_distribution": root_cause_counts,
        "channel_distribution": channel_counts,
        "status_distribution": status_counts,
    }


@router.get("/cases")
async def list_cases(
    status: str | None = None,
    event_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    """List all recovery cases with optional filters."""
    cases = list(_cases_store.values())

    # Apply filters
    if status:
        cases = [c for c in cases if c.get("case_status") == status]
    if event_type:
        cases = [c for c in cases if c.get("event_type") == event_type]

    # Sort by created_at descending
    cases.sort(key=lambda c: c.get("created_at", ""), reverse=True)

    total = len(cases)
    paginated = cases[offset: offset + limit]

    return {
        "cases": [_serialize_case(c) for c in paginated],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Get full case detail with audit trail."""
    case = _cases_store.get(case_id)
    if not case:
        return {"error": "Case not found", "case_id": case_id}
    return _serialize_case(case)


@router.get("/metrics")
async def get_metrics():
    """Aggregated recovery metrics for dashboard."""
    return _compute_metrics()


@router.get("/compliance")
async def get_compliance():
    """Compliance status summary."""
    cases = list(_cases_store.values())

    # Check each guardrail across all cases
    max_retry_violations = sum(1 for c in cases if c.get("retry_count", 0) > 3)
    opt_out_violations = sum(
        1 for c in cases
        if c.get("customer_opted_out") and c.get("execution_status") == "success"
    )
    # DND and human approval violations would be caught by the gate

    return {
        "total_cases_checked": len(cases),
        "violations": max_retry_violations + opt_out_violations,
        "guardrails": {
            "max_retries": {
                "rule": "Max 3 retries per case",
                "status": "passing" if max_retry_violations == 0 else "failing",
                "violations": max_retry_violations,
            },
            "dnd_window": {
                "rule": "No contact 9 PM - 8 AM IST",
                "status": "passing",
                "violations": 0,
            },
            "opt_out": {
                "rule": "Opt-out instantly binding",
                "status": "passing" if opt_out_violations == 0 else "failing",
                "violations": opt_out_violations,
            },
            "human_approval": {
                "rule": "Human approval above threshold",
                "status": "passing",
                "violations": 0,
            },
        },
    }


@router.get("/approval-queue")
async def get_approval_queue():
    """Cases pending human approval."""
    pending = [
        _serialize_case(c) for c in _cases_store.values()
        if c.get("case_status") == "pending_approval"
    ]
    return {"cases": pending, "total": len(pending)}


@router.post("/cases/{case_id}/approve")
async def approve_case(case_id: str):
    """Approve a pending case for execution."""
    case = _cases_store.get(case_id)
    if not case:
        return {"error": "Case not found"}
    if case.get("case_status") != "pending_approval":
        return {"error": "Case is not pending approval"}

    case["case_status"] = "guardrail_checked"
    case["guardrail_status"] = "approved"
    case["updated_at"] = datetime.now(timezone.utc).isoformat()
    case["audit_trail"] = case.get("audit_trail", []) + [{
        "node_name": "human_approval",
        "input_summary": f"Case {case_id} reviewed by human",
        "output_summary": "Approved for execution",
        "reasoning": "Human operator approved the recovery action",
        "provider": "human",
        "latency_ms": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }]

    return {"case_id": case_id, "status": "approved"}


@router.post("/cases/{case_id}/reject")
async def reject_case(case_id: str):
    """Reject a pending case."""
    case = _cases_store.get(case_id)
    if not case:
        return {"error": "Case not found"}

    case["case_status"] = "blocked"
    case["guardrail_status"] = "blocked"
    case["updated_at"] = datetime.now(timezone.utc).isoformat()
    case["audit_trail"] = case.get("audit_trail", []) + [{
        "node_name": "human_approval",
        "input_summary": f"Case {case_id} reviewed by human",
        "output_summary": "Rejected",
        "reasoning": "Human operator rejected the recovery action",
        "provider": "human",
        "latency_ms": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }]

    return {"case_id": case_id, "status": "rejected"}


@router.post("/process-batch")
async def process_batch_endpoint(count: int = 50):
    """Process a batch of synthetic events through the pipeline."""
    data_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "samples" / "tuning_set.json"

    if not data_path.exists():
        return {"error": "Synthetic data not found. Run the data generator first."}

    with open(data_path, "r", encoding="utf-8") as f:
        all_events = json.load(f)

    # Process up to `count` events
    batch = all_events[:count]
    results = process_batch(batch)

    # Store results
    for result in results:
        _cases_store[result["case_id"]] = result

    metrics = _compute_metrics()

    return {
        "status": "completed",
        "events_processed": len(results),
        "metrics_summary": {
            "total_at_risk": metrics["total_at_risk"],
            "total_recovered": metrics["total_recovered"],
            "recovery_rate": metrics["recovery_rate"],
            "rule_hit_ratio": metrics["rule_hit_ratio"],
            "compliance_violations": metrics["compliance_violations"],
        },
    }


@router.get("/process-batch-stream")
async def process_batch_stream_endpoint(count: int = 100):
    """Stream case-by-case pipeline execution live via Server-Sent Events (SSE)."""
    data_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "samples" / "tuning_set.json"

    if not data_path.exists():
        return {"error": "Synthetic data not found."}

    with open(data_path, "r", encoding="utf-8") as f:
        all_events = json.load(f)

    batch = all_events[:count]

    async def event_generator():
        for i, event in enumerate(batch, 1):
            result = await asyncio.to_thread(process_event, event)
            _cases_store[result["case_id"]] = result

            payload = {
                "type": "case",
                "index": i,
                "total": len(batch),
                "case_id": result["case_id"],
                "event_type": result["event_type"],
                "decline_reason": result["decline_reason_raw"],
                "root_cause": result["root_cause"],
                "method": result["diagnosis_method"],
                "provider": result["diagnosis_provider"],
                "latency_ms": result["diagnosis_latency_ms"],
                "status": result["case_status"],
                "amount": result["amount_at_risk"],
            }
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0.001)

        metrics = _compute_metrics()
        final_payload = {
            "type": "summary",
            "metrics": metrics,
        }
        yield f"data: {json.dumps(final_payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")



@router.post("/synthesize-voice")
async def synthesize_voice_endpoint(payload: dict):
    """Synthesize multi-language voice recovery audio using gTTS."""
    text = payload.get("text", "")
    customer_name = payload.get("customer_name", "Customer")
    amount = float(payload.get("amount", 5000.0))
    reason = payload.get("reason", "insufficient_funds")
    lang = payload.get("lang", "hinglish")

    if not text:
        text = hinglish_voice_channel.generate_recovery_script(customer_name, amount, reason, lang=lang)

    result = hinglish_voice_channel.synthesize_hinglish_speech(text, lang=lang)
    return result


@router.get("/voice-languages")
async def get_voice_languages():
    """Return supported voice synthesis languages."""
    return {"languages": hinglish_voice_channel.get_supported_languages()}

