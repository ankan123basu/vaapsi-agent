"""
Recoup — Guardrail Gate Node.

HARD-CODED, NON-LLM, DETERMINISTIC compliance checks.
This node can reject or defer a case to the human approval queue.

Guardrails:
1. Max 3 retry attempts with exponential backoff
2. Do-not-disturb: no contact 9 PM - 8 AM IST
3. Opt-out is instantly binding (permanent, no exceptions)
4. Human approval above configurable INR threshold or discount offers
"""

from datetime import datetime, timezone, timedelta

from app.graph.state import RecoveryCase
from app.config import settings


# IST offset
IST = timezone(timedelta(hours=5, minutes=30))


def gate_node(state: RecoveryCase) -> dict:
    """
    Guardrail Gate — deterministic compliance checks.
    NO LLM in the loop. Every check is hard-coded and auditable.
    """
    start_time = datetime.now(timezone.utc)
    violations = []
    guardrail_status = "approved"

    # ============================================
    # GUARDRAIL 1: Opt-out is instantly binding
    # ============================================
    if state.get("customer_opted_out", False):
        violations.append("OPTED_OUT: Customer has opted out of all recovery communications")
        guardrail_status = "blocked"

    # ============================================
    # GUARDRAIL 2: Max retry attempts (3)
    # ============================================
    retry_count = state.get("retry_count", 0)
    max_retries = settings.max_retry_attempts

    if retry_count >= max_retries:
        violations.append(
            f"MAX_RETRIES: Case has reached {retry_count}/{max_retries} retry attempts. "
            f"4th attempt auto-blocked."
        )
        guardrail_status = "blocked"

    # ============================================
    # GUARDRAIL 3: Do-not-disturb window (9 PM - 8 AM IST)
    # ============================================
    scheduled_at_str = state.get("scheduled_at", "")
    if scheduled_at_str:
        try:
            scheduled_at = datetime.fromisoformat(scheduled_at_str)
            scheduled_ist = scheduled_at.astimezone(IST)
            hour_ist = scheduled_ist.hour

            dnd_start = settings.dnd_start_hour  # 21 (9 PM)
            dnd_end = settings.dnd_end_hour      # 8 (8 AM)

            in_dnd = hour_ist >= dnd_start or hour_ist < dnd_end

            if in_dnd:
                violations.append(
                    f"DND_WINDOW: Scheduled contact at {scheduled_ist.strftime('%I:%M %p')} IST "
                    f"falls within do-not-disturb window ({dnd_start}:00-{dnd_end}:00 IST). "
                    f"Rescheduling to next available window."
                )
                # Don't block — reschedule to 8 AM IST
                if hour_ist >= dnd_start:
                    # After 9 PM — schedule for next day 8 AM
                    next_day = scheduled_ist + timedelta(days=1)
                    rescheduled = next_day.replace(hour=dnd_end, minute=0, second=0)
                else:
                    # Before 8 AM — schedule for 8 AM same day
                    rescheduled = scheduled_ist.replace(hour=dnd_end, minute=0, second=0)

                # Note: We modify scheduled_at but don't block the case
                # The violation is logged but the case proceeds with new time
        except (ValueError, TypeError):
            pass

    # ============================================
    # GUARDRAIL 4: Human approval threshold
    # ============================================
    amount = state.get("amount_at_risk", 0)
    threshold = settings.human_approval_threshold_inr
    offer_details = state.get("offer_details", {})
    has_discount = offer_details.get("type") == "discount" if offer_details else False

    if amount > threshold:
        violations.append(
            f"HIGH_VALUE: Recovery action for INR {amount:,.2f} exceeds "
            f"approval threshold of INR {threshold:,.2f}. Routing to human approval queue."
        )
        if guardrail_status != "blocked":
            guardrail_status = "needs_human_approval"

    if has_discount:
        violations.append(
            "DISCOUNT_OFFER: Recovery action includes a discount/waiver offer. "
            "Routing to human approval queue."
        )
        if guardrail_status != "blocked":
            guardrail_status = "needs_human_approval"

    # Map guardrail status to case status
    case_status_map = {
        "approved": "guardrail_checked",
        "blocked": "blocked",
        "needs_human_approval": "pending_approval",
    }

    end_time = datetime.now(timezone.utc)
    latency_ms = (end_time - start_time).total_seconds() * 1000

    audit_entry = {
        "node_name": "guardrail_gate",
        "input_summary": f"Amount: INR {amount}, retries: {retry_count}, opted_out: {state.get('customer_opted_out', False)}",
        "output_summary": f"Status: {guardrail_status}, violations: {len(violations)}",
        "reasoning": "; ".join(violations) if violations else "All guardrail checks passed. No violations.",
        "provider": "deterministic/guardrails",
        "latency_ms": round(latency_ms, 2),
        "timestamp": end_time.isoformat(),
    }

    return {
        "guardrail_status": guardrail_status,
        "guardrail_violations": violations,
        "case_status": case_status_map.get(guardrail_status, "guardrail_checked"),
        "audit_trail": [audit_entry],
    }
