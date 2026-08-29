"""
Recoup — Detector Node.

Classifies incoming events into: payment_failed, checkout_abandoned, mandate_failed.
Extracts the raw failure/decline reason if present.
"""

import uuid
from datetime import datetime, timezone

from app.graph.state import RecoveryCase


def detector_node(state: RecoveryCase) -> dict:
    """
    Detector node — classifies the incoming event and extracts key fields.

    Input: raw_event in state
    Output: event_type, decline_reason_raw, customer details, amount_at_risk
    """
    start_time = datetime.now(timezone.utc)
    raw_event = state["raw_event"]
    event_type = raw_event.get("event_type", "unknown")

    # Extract common fields
    customer = raw_event.get("customer", {})
    customer_id = customer.get("id", f"cust_unknown_{uuid.uuid4().hex[:8]}")
    customer_email = customer.get("email", "")
    customer_phone = customer.get("phone", "")
    customer_name = customer.get("name", "")

    # Extract event-type-specific fields
    decline_reason_raw = ""
    amount_at_risk = 0.0

    if event_type == "payment_failed":
        decline_reason_raw = raw_event.get("decline_code", "") or raw_event.get("decline_reason", "")
        amount_at_risk = raw_event.get("amount", 0.0)

    elif event_type == "checkout_abandoned":
        decline_reason_raw = "checkout_abandoned"
        amount_at_risk = raw_event.get("cart_value", 0.0)

    elif event_type == "mandate_failed":
        decline_reason_raw = raw_event.get("failure_reason", "")
        amount_at_risk = raw_event.get("amount", 0.0)

    end_time = datetime.now(timezone.utc)
    latency_ms = (end_time - start_time).total_seconds() * 1000

    # Build audit entry
    audit_entry = {
        "node_name": "detector",
        "input_summary": f"Event {raw_event.get('event_id', 'unknown')} of type {event_type}",
        "output_summary": f"Classified as {event_type}, decline_reason={decline_reason_raw}, amount={amount_at_risk}",
        "reasoning": "Direct field extraction from raw event payload",
        "provider": "deterministic",
        "latency_ms": round(latency_ms, 2),
        "timestamp": end_time.isoformat(),
    }

    return {
        "event_type": event_type,
        "customer_id": customer_id,
        "customer_email": customer_email,
        "customer_phone": customer_phone,
        "customer_name": customer_name,
        "decline_reason_raw": decline_reason_raw,
        "amount_at_risk": amount_at_risk,
        "currency": raw_event.get("currency", "INR"),
        "detected_at": end_time.isoformat(),
        "case_status": "detected",
        "audit_trail": [audit_entry],
    }
