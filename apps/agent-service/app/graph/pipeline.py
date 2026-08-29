"""
Recoup — LangGraph Pipeline Assembly.

Connects all 7 nodes into a StateGraph with conditional routing.

Flow:
    Detector → Diagnoser → Strategist → Gate → (branch)
        → approved: Executor → Auditor → Reporter
        → blocked: Reporter (skip execution)
        → needs_human_approval: Reporter (park in queue)
"""

import uuid
from datetime import datetime, timezone

from langgraph.graph import StateGraph, END

from app.graph.state import RecoveryCase
from app.graph.detector import detector_node
from app.graph.diagnoser import diagnoser_node
from app.graph.strategist import strategist_node
from app.graph.gate import gate_node
from app.graph.executor import executor_node
from app.graph.auditor import auditor_node
from app.graph.reporter import reporter_node


def _route_after_gate(state: RecoveryCase) -> str:
    """
    Conditional routing after the Guardrail Gate.
    - approved → executor
    - blocked → reporter (skip execution, log why)
    - needs_human_approval → reporter (park in queue)
    """
    guardrail_status = state.get("guardrail_status", "approved")

    if guardrail_status == "approved":
        return "executor"
    else:
        # Both "blocked" and "needs_human_approval" skip execution
        return "reporter"


def build_recovery_graph() -> StateGraph:
    """
    Build the full LangGraph recovery pipeline.

    Returns a compiled StateGraph ready to invoke.
    """
    graph = StateGraph(RecoveryCase)

    # Add all nodes
    graph.add_node("detector", detector_node)
    graph.add_node("diagnoser", diagnoser_node)
    graph.add_node("strategist", strategist_node)
    graph.add_node("gate", gate_node)
    graph.add_node("executor", executor_node)
    graph.add_node("auditor", auditor_node)
    graph.add_node("reporter", reporter_node)

    # Set entry point
    graph.set_entry_point("detector")

    # Linear flow: Detector → Diagnoser → Strategist → Gate
    graph.add_edge("detector", "diagnoser")
    graph.add_edge("diagnoser", "strategist")
    graph.add_edge("strategist", "gate")

    # Conditional routing after Gate
    graph.add_conditional_edges(
        "gate",
        _route_after_gate,
        {
            "executor": "executor",
            "reporter": "reporter",
        },
    )

    # After executor → auditor → reporter
    graph.add_edge("executor", "auditor")
    graph.add_edge("auditor", "reporter")

    # Reporter is the terminal node
    graph.add_edge("reporter", END)

    return graph.compile()


# Pre-compiled graph instance
recovery_pipeline = build_recovery_graph()


def process_event(raw_event: dict) -> RecoveryCase:
    """
    Process a single event through the full recovery pipeline.

    This is the main entry point — takes a raw event dict,
    returns the fully processed RecoveryCase with complete audit trail.
    """
    now = datetime.now(timezone.utc).isoformat()

    # Initialize case state
    initial_state: RecoveryCase = {
        "case_id": f"case_{uuid.uuid4().hex[:12]}",
        "event_id": raw_event.get("event_id", f"evt_{uuid.uuid4().hex[:12]}"),
        "event_type": raw_event.get("event_type", "unknown"),
        "raw_event": raw_event,
        "customer_id": "",
        "customer_email": "",
        "customer_phone": "",
        "customer_name": "",
        "customer_opted_out": False,
        "amount_at_risk": 0.0,
        "currency": "INR",
        "decline_reason_raw": "",
        "root_cause": "",
        "root_cause_confidence": 0.0,
        "diagnosis_method": "",
        "diagnosis_reasoning": "",
        "diagnosis_provider": "",
        "diagnosis_latency_ms": 0.0,
        "recovery_channel": "",
        "recovery_action": "",
        "message_content": "",
        "offer_details": {},
        "scheduled_at": "",
        "guardrail_status": "",
        "guardrail_violations": [],
        "execution_status": "",
        "execution_result": {},
        "razorpay_payment_link_id": "",
        "recovery_amount": 0.0,
        "case_status": "detected",
        "retry_count": 0,
        "idempotency_key": raw_event.get("event_id", ""),
        "audit_trail": [],
        "created_at": now,
        "updated_at": now,
    }

    # Run through the pipeline
    result = recovery_pipeline.invoke(initial_state)

    return result


def process_batch(events: list[dict]) -> list[RecoveryCase]:
    """
    Process a batch of events through the pipeline.

    Returns a list of processed RecoveryCases.
    """
    results = []
    for event in events:
        result = process_event(event)
        results.append(result)
    return results
