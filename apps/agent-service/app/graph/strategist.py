"""
Recoup — Strategist Node (Policy Engine + Message Drafting).

The DECISION of whether to act, on what channel, and how aggressively
is a deterministic policy table. The LLM is used ONLY for message content drafting.
"""

from datetime import datetime, timezone, timedelta

from app.graph.state import RecoveryCase
from app.classifiers.root_causes import RETRYABLE_ROOT_CAUSES, NEEDS_NEW_INSTRUMENT, RootCause


# ============================================
# DETERMINISTIC POLICY TABLE
# ============================================
# The LLM does NOT decide the policy — it only drafts the message.
# ============================================

RECOVERY_POLICY = {
    "insufficient_funds": {
        "channel": "payment_link",
        "action": "send_payment_link",
        "tone": "empathetic",
        "delay_hours": 4,
        "message_template": "We noticed your payment of {amount} didn't go through. We've created a new payment link for when you're ready.",
    },
    "expired_instrument": {
        "channel": "email",
        "action": "request_card_update",
        "tone": "informative",
        "delay_hours": 1,
        "message_template": "Your payment instrument on file has expired. Please update your card details to complete your purchase of {amount}.",
    },
    "issuer_unavailable": {
        "channel": "payment_link",
        "action": "auto_retry_with_link",
        "tone": "reassuring",
        "delay_hours": 2,
        "message_template": "Your bank was temporarily unavailable when you tried to pay. Here's a fresh link to try again — the issue should be resolved now.",
    },
    "risk_declined": {
        "channel": "email",
        "action": "suggest_alternative_method",
        "tone": "professional",
        "delay_hours": 6,
        "message_template": "Your payment was flagged by your bank's security system. You may want to try a different payment method, or contact your bank to authorize this transaction.",
    },
    "authentication_failed": {
        "channel": "sms",
        "action": "send_payment_link",
        "tone": "helpful",
        "delay_hours": 0.5,
        "message_template": "Your OTP/authentication timed out. Here's a quick link to try again — keep your phone ready for the OTP.",
    },
    "invalid_details": {
        "channel": "payment_link",
        "action": "send_payment_link",
        "tone": "helpful",
        "delay_hours": 0.5,
        "message_template": "There was an issue with the payment details entered. Please try again with the correct information.",
    },
    "network_error": {
        "channel": "payment_link",
        "action": "auto_retry_with_link",
        "tone": "reassuring",
        "delay_hours": 1,
        "message_template": "A network issue interrupted your payment. Here's a fresh link — the connectivity issue should be resolved.",
    },
    "limit_exceeded": {
        "channel": "email",
        "action": "suggest_alternative_method",
        "tone": "informative",
        "delay_hours": 12,
        "message_template": "Your payment exceeded your card's transaction limit. You can try with a different card or payment method.",
    },
    "customer_action_needed": {
        "channel": "email",
        "action": "notify_action_required",
        "tone": "professional",
        "delay_hours": 2,
        "message_template": "Your payment requires action on your end. Please contact your bank or update your payment details.",
    },
    "mandate_issue": {
        "channel": "email",
        "action": "request_mandate_reauthorization",
        "tone": "professional",
        "delay_hours": 24,
        "message_template": "Your subscription payment couldn't be processed. Please reauthorize your payment mandate to continue your plan.",
    },
    "checkout_friction": {
        "channel": "email",
        "action": "send_cart_reminder",
        "tone": "friendly",
        "delay_hours": 1,
        "message_template": "You left some items in your cart worth {amount}. Here's a direct link to complete your purchase.",
    },
    "unknown": {
        "channel": "email",
        "action": "gentle_reminder",
        "tone": "professional",
        "delay_hours": 6,
        "message_template": "We noticed your recent payment didn't complete. If you'd like to try again, here's a link.",
    },
}


def strategist_node(state: RecoveryCase) -> dict:
    """
    Strategist node — deterministic policy decision + message content.

    The POLICY is deterministic (channel, action, timing).
    Message content uses the template — LLM drafting is optional enhancement.
    """
    start_time = datetime.now(timezone.utc)

    root_cause = state.get("root_cause", "unknown")
    amount = state.get("amount_at_risk", 0)
    currency = state.get("currency", "INR")
    customer_name = state.get("customer_name", "Customer")
    event_type = state.get("event_type", "payment_failed")

    # Look up policy
    policy = RECOVERY_POLICY.get(root_cause, RECOVERY_POLICY["unknown"])

    # Format message from template
    message = policy["message_template"].format(
        amount=f"{currency} {amount:,.2f}",
        name=customer_name,
    )

    # Calculate scheduled time
    delay = timedelta(hours=policy["delay_hours"])
    scheduled_at = (start_time + delay).isoformat()

    # Check if this root cause might warrant an offer/discount
    offer_details = {}
    if event_type == "checkout_abandoned" and amount > 2000:
        offer_details = {
            "type": "reminder",
            "note": "High-value cart — consider offering free shipping if available",
        }

    end_time = datetime.now(timezone.utc)
    latency_ms = (end_time - start_time).total_seconds() * 1000

    audit_entry = {
        "node_name": "strategist",
        "input_summary": f"Root cause: {root_cause}, amount: {currency} {amount}",
        "output_summary": f"Channel: {policy['channel']}, action: {policy['action']}, scheduled in {policy['delay_hours']}h",
        "reasoning": f"Policy table lookup for '{root_cause}': channel={policy['channel']}, tone={policy['tone']}, delay={policy['delay_hours']}h. LLM authority: message drafting only, not policy decisions.",
        "provider": "deterministic/policy_table",
        "latency_ms": round(latency_ms, 2),
        "timestamp": end_time.isoformat(),
    }

    return {
        "recovery_channel": policy["channel"],
        "recovery_action": policy["action"],
        "message_content": message,
        "offer_details": offer_details,
        "scheduled_at": scheduled_at,
        "case_status": "strategy_set",
        "audit_trail": [audit_entry],
    }
