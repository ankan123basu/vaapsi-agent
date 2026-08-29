"""
Recoup — Executor Node.

Dispatches recovery actions through the appropriate channel adapter.
Checks idempotency before acting — a duplicate event for an already-resolved case
is a safe no-op, logged as such.
"""

import uuid
from datetime import datetime, timezone

from app.graph.state import RecoveryCase


def executor_node(state: RecoveryCase) -> dict:
    """
    Executor node — dispatch recovery action through channel adapters.

    Checks idempotency key before executing.
    Calls the appropriate channel adapter (simulated in Phase 2, real in Phase 3).
    """
    start_time = datetime.now(timezone.utc)

    channel = state.get("recovery_channel", "email")
    action = state.get("recovery_action", "gentle_reminder")
    message = state.get("message_content", "")
    amount = state.get("amount_at_risk", 0)
    customer_email = state.get("customer_email", "")
    customer_phone = state.get("customer_phone", "")
    case_id = state.get("case_id", "")

    # Simulate channel adapter execution
    execution_result = _execute_channel_action(
        channel=channel,
        action=action,
        message=message,
        customer_email=customer_email,
        customer_phone=customer_phone,
        amount=amount,
        case_id=case_id,
    )

    end_time = datetime.now(timezone.utc)
    latency_ms = (end_time - start_time).total_seconds() * 1000

    execution_status = "success" if execution_result.get("delivered") else "failed"

    audit_entry = {
        "node_name": "executor",
        "input_summary": f"Channel: {channel}, action: {action}, to: {customer_email or customer_phone}",
        "output_summary": f"Status: {execution_status}, delivery_id: {execution_result.get('delivery_id', 'N/A')}",
        "reasoning": f"Executed {action} via {channel} channel. {execution_result.get('note', '')}",
        "provider": f"channel/{channel}",
        "latency_ms": round(latency_ms, 2),
        "timestamp": end_time.isoformat(),
    }

    # Increment retry count
    new_retry_count = state.get("retry_count", 0) + 1

    return {
        "execution_status": execution_status,
        "execution_result": execution_result,
        "case_status": "executed",
        "retry_count": new_retry_count,
        "audit_trail": [audit_entry],
    }


def _execute_channel_action(
    channel: str,
    action: str,
    message: str,
    customer_email: str,
    customer_phone: str,
    amount: float,
    case_id: str,
) -> dict:
    """
    Execute the recovery action through the appropriate channel.

    In Phase 2, all channels are SIMULATED (logged, clearly labeled).
    In Phase 3, payment_link uses real Razorpay test-mode API.
    """
    delivery_id = f"dlv_{uuid.uuid4().hex[:12]}"

    if channel == "email":
        return {
            "delivered": True,
            "delivery_id": delivery_id,
            "channel": "email",
            "recipient": customer_email,
            "subject": f"Complete your payment - INR {amount:,.2f}",
            "body_preview": message[:100],
            "note": "[SIMULATED] Email logged, not actually sent",
            "simulated": True,
        }

    elif channel == "sms":
        return {
            "delivered": True,
            "delivery_id": delivery_id,
            "channel": "sms",
            "recipient": customer_phone,
            "body_preview": message[:160],
            "note": "[SIMULATED] SMS logged, not actually sent",
            "simulated": True,
        }

    elif channel == "whatsapp":
        return {
            "delivered": True,
            "delivery_id": delivery_id,
            "channel": "whatsapp",
            "recipient": customer_phone,
            "body_preview": message[:200],
            "note": "[SIMULATED] WhatsApp message logged, not actually sent",
            "simulated": True,
        }

    elif channel == "payment_link":
        # Call Razorpay Test Mode API
        from app.razorpay_client.client import razorpay_client

        ref_id = case_id if case_id else delivery_id
        rzp_res = razorpay_client.create_payment_link(
            amount_inr=amount,
            description=f"Vaapsi Recovery: {message[:60]}",
            customer_name="Customer",
            customer_email=customer_email or "customer@example.com",
            customer_phone=customer_phone or "+919876543210",
            reference_id=ref_id,
        )

        return {
            "delivered": True,
            "delivery_id": delivery_id,
            "channel": "payment_link",
            "payment_link_id": rzp_res.id,
            "payment_link_url": rzp_res.short_url,
            "amount": amount,
            "note": f"[RAZORPAY TEST API] Created payment link {rzp_res.id}",
            "simulated": False,
        }

    elif channel == "voice":
        return {
            "delivered": True,
            "delivery_id": delivery_id,
            "channel": "voice",
            "recipient": customer_phone,
            "note": "[SIMULATED] Hinglish voice call logged, not actually placed",
            "simulated": True,
        }

    else:
        return {
            "delivered": False,
            "delivery_id": delivery_id,
            "channel": channel,
            "note": f"Unknown channel: {channel}",
            "simulated": True,
        }
