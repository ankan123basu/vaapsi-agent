"""
Recoup — Diagnoser Node (Root-Cause Classifier).

HYBRID: Rules layer first (deterministic), LLM fallback only for residuals.
Logs which layer made the call for every case.
"""

from datetime import datetime, timezone

from app.graph.state import RecoveryCase
from app.classifiers.rules_engine import classify_with_rules
from app.classifiers.llm_classifier import classify_with_llm


def diagnoser_node(state: RecoveryCase) -> dict:
    """
    Diagnoser node — hybrid root-cause classification.

    1. Try rules engine first (deterministic, fast)
    2. Fall back to LLM only for ambiguous/unknown codes
    3. Log which layer + provider handled the call
    """
    start_time = datetime.now(timezone.utc)
    decline_reason = state.get("decline_reason_raw", "")
    event_type = state.get("event_type", "payment_failed")
    raw_event = state.get("raw_event", {})
    method = raw_event.get("method", "card")
    bank = raw_event.get("bank", "unknown")

    # Step 1: Try rules engine first
    rules_result = classify_with_rules(decline_reason, event_type)

    if rules_result.matched:
        # Rules engine handled it — no LLM call needed
        end_time = datetime.now(timezone.utc)
        latency_ms = (end_time - start_time).total_seconds() * 1000

        audit_entry = {
            "node_name": "diagnoser",
            "input_summary": f"Decline reason: '{decline_reason}' for {event_type}",
            "output_summary": f"Root cause: {rules_result.root_cause} (confidence: {rules_result.confidence:.2f})",
            "reasoning": f"[RULE HIT] {rules_result.reasoning}",
            "provider": "deterministic/rules_engine",
            "latency_ms": round(latency_ms, 2),
            "timestamp": end_time.isoformat(),
        }

        return {
            "root_cause": rules_result.root_cause,
            "root_cause_confidence": rules_result.confidence,
            "diagnosis_method": "rule",
            "diagnosis_reasoning": rules_result.reasoning,
            "diagnosis_provider": "deterministic/rules_engine",
            "diagnosis_latency_ms": round(latency_ms, 2),
            "case_status": "diagnosed",
            "audit_trail": [audit_entry],
        }

    # Step 2: LLM fallback for ambiguous codes
    llm_result = classify_with_llm(decline_reason, event_type, method, bank)

    end_time = datetime.now(timezone.utc)
    latency_ms = (end_time - start_time).total_seconds() * 1000

    audit_entry = {
        "node_name": "diagnoser",
        "input_summary": f"Decline reason: '{decline_reason}' for {event_type}",
        "output_summary": f"Root cause: {llm_result.root_cause} (confidence: {llm_result.confidence:.2f})",
        "reasoning": f"[LLM FALLBACK] {llm_result.reasoning} — answered by {llm_result.provider} in {llm_result.latency_ms:.0f}ms",
        "provider": llm_result.provider,
        "latency_ms": round(latency_ms, 2),
        "timestamp": end_time.isoformat(),
    }

    return {
        "root_cause": llm_result.root_cause,
        "root_cause_confidence": llm_result.confidence,
        "diagnosis_method": "llm_fallback",
        "diagnosis_reasoning": llm_result.reasoning,
        "diagnosis_provider": llm_result.provider,
        "diagnosis_latency_ms": round(latency_ms, 2),
        "case_status": "diagnosed",
        "audit_trail": [audit_entry],
    }
