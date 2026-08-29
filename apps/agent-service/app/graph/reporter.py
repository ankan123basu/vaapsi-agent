"""
Recoup — Reporter Node.

Aggregates recovery metrics for the dashboard.
This node is a passive reader — it doesn't modify the case.
"""

from datetime import datetime, timezone

from app.graph.state import RecoveryCase


def reporter_node(state: RecoveryCase) -> dict:
    """
    Reporter node — collects metrics for dashboard reporting.
    This is the final node in the pipeline.
    """
    end_time = datetime.now(timezone.utc)

    audit_entry = {
        "node_name": "reporter",
        "input_summary": f"Case {state.get('case_id', '')} finalized as {state.get('case_status', 'unknown')}",
        "output_summary": f"Recovery: INR {state.get('recovery_amount', 0):,.2f} of INR {state.get('amount_at_risk', 0):,.2f}",
        "reasoning": "Case processing complete. Metrics updated for dashboard.",
        "provider": "deterministic/reporter",
        "latency_ms": 0,
        "timestamp": end_time.isoformat(),
    }

    return {
        "updated_at": end_time.isoformat(),
        "audit_trail": [audit_entry],
    }
