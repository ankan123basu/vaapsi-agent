"""
Recoup — Nuisance-Suppression Scorer Node.

Scores each case's probability of self-resolving without intervention.
When probability exceeds threshold (0.70), contact is suppressed to avoid
unnecessary customer disturbance.

Approach: Documented, defensible heuristic scorer using signals already
present in RecoveryCase (root cause category, retry count, time elapsed
since failure). This is more honest under questioning than an undertrained
ML model — each weight has a clear rationale.

Heuristic Scoring Table:
┌────────────────────────────┬─────────┬────────────────────────────────────────────────────┐
│ Signal                     │ Weight  │ Rationale                                          │
├────────────────────────────┼─────────┼────────────────────────────────────────────────────┤
│ network_error              │ +0.50   │ Transient; gateway/CDN/DNS issues resolve quickly  │
│ issuer_unavailable         │ +0.45   │ Bank downtime is temporary; comes back online      │
│ authentication_failed      │ +0.15   │ Customer often retries OTP/3DS immediately         │
│ checkout_friction          │ +0.10   │ Customer may return if browsing/comparing           │
│ insufficient_funds         │ +0.05   │ Rarely self-resolves (customer needs more money)    │
│ All other root causes      │ +0.00   │ Expired card, risk blocks need customer action      │
├────────────────────────────┼─────────┼────────────────────────────────────────────────────┤
│ retry_count > 1            │ −0.15   │ Repeated failure = unlikely to self-resolve         │
│ time_since_failure < 30min │ +0.20   │ Very recent; customer likely still at checkout      │
│ time_since_failure > 24h   │ −0.10   │ Stale failure; customer has moved on                │
└────────────────────────────┴─────────┴────────────────────────────────────────────────────┘

Threshold: self_resolution_probability > 0.55 → suppress contact.
"""

from datetime import datetime, timezone, timedelta

from app.graph.state import RecoveryCase


# Suppression threshold — above this, contact is withheld
SUPPRESSION_THRESHOLD = 0.55

# Root-cause base scores — probability of self-resolution by category
ROOT_CAUSE_BASE_SCORES: dict[str, float] = {
    "network_error": 0.50,
    "issuer_unavailable": 0.45,
    "authentication_failed": 0.15,
    "checkout_friction": 0.10,
    "insufficient_funds": 0.05,
}


def _parse_timestamp(ts: str) -> datetime | None:
    """Safely parse an ISO timestamp string."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def suppression_node(state: RecoveryCase) -> dict:
    """
    Nuisance-Suppression Scorer — scores each case's probability of
    self-resolving without any recovery action.

    When probability is high (> 0.70), the case is routed to "monitor,
    no contact" instead of active recovery. This avoids unnecessary
    customer disturbance for transient issues.

    Uses a documented heuristic scorer — NOT an ML model. Each weight
    has a clear, defensible rationale documented in the module docstring.
    """
    start_time = datetime.now(timezone.utc)

    root_cause = state.get("root_cause", "unknown")
    retry_count = state.get("retry_count", 0)
    detected_at_str = state.get("detected_at", "")
    event_type = state.get("event_type", "payment_failed")

    # ── Step 1: Base score from root cause ────────────────────────
    base_score = ROOT_CAUSE_BASE_SCORES.get(root_cause, 0.0)
    reasoning_parts = []

    if base_score > 0:
        reasoning_parts.append(
            f"Root cause '{root_cause}' has base self-resolution probability of {base_score:.2f}"
        )
    else:
        reasoning_parts.append(
            f"Root cause '{root_cause}' has no inherent self-resolution tendency (base=0.00)"
        )

    # ── Step 2: Retry count adjustment ────────────────────────────
    retry_adj = 0.0
    if retry_count > 1:
        retry_adj = -0.15
        reasoning_parts.append(
            f"Retry count {retry_count} > 1 → repeated failure penalty ({retry_adj:+.2f})"
        )

    # ── Step 3: Freshness adjustment ──────────────────────────────
    # Instead of comparing timestamps (unreliable in batch mode due to
    # wall-clock vs. event-time mismatch), we use retry count and event
    # metadata as a proxy for how "fresh" the failure is.
    time_adj = 0.0

    # First-attempt failures are most likely to self-resolve
    if retry_count == 0:
        # Check if it's a mandate with high attempt_number
        raw_event = state.get("raw_event", {})
        attempt_number = raw_event.get("attempt_number", 1)
        if attempt_number <= 1:
            time_adj = 0.20
            reasoning_parts.append(
                f"First attempt (retry=0, attempt={attempt_number}) → recency bonus ({time_adj:+.2f})"
            )
        elif attempt_number >= 3:
            time_adj = -0.10
            reasoning_parts.append(
                f"Multiple prior attempts (attempt={attempt_number}) → staleness penalty ({time_adj:+.2f})"
            )
    elif retry_count >= 2:
        time_adj = -0.10
        reasoning_parts.append(
            f"High retry count ({retry_count}) → staleness penalty ({time_adj:+.2f})"
        )

    # ── Step 4: Compute final score ───────────────────────────────
    raw_probability = base_score + retry_adj + time_adj
    # Clamp to [0.0, 1.0]
    probability = max(0.0, min(1.0, raw_probability))

    # ── Step 5: Suppression decision ──────────────────────────────
    suppressed = probability > SUPPRESSION_THRESHOLD

    if suppressed:
        reasoning_parts.append(
            f"SUPPRESSED: Score {probability:.2f} > threshold {SUPPRESSION_THRESHOLD} → "
            f"monitoring only, no customer contact. Likely self-resolving."
        )
    else:
        reasoning_parts.append(
            f"NOT suppressed: Score {probability:.2f} ≤ threshold {SUPPRESSION_THRESHOLD} → "
            f"proceeding with active recovery."
        )

    full_reasoning = "; ".join(reasoning_parts)

    end_time = datetime.now(timezone.utc)
    latency_ms = (end_time - start_time).total_seconds() * 1000

    audit_entry = {
        "node_name": "suppression_scorer",
        "input_summary": f"Root cause: {root_cause}, retry: {retry_count}, event_type: {event_type}",
        "output_summary": f"Self-resolution prob: {probability:.2f}, suppressed: {suppressed}",
        "reasoning": full_reasoning,
        "provider": "deterministic/heuristic_scorer",
        "latency_ms": round(latency_ms, 2),
        "timestamp": end_time.isoformat(),
    }

    result = {
        "self_resolution_probability": round(probability, 4),
        "contact_suppressed": suppressed,
        "suppression_reasoning": full_reasoning,
        "audit_trail": [audit_entry],
    }

    # If suppressed, set terminal status
    if suppressed:
        result["case_status"] = "suppressed"

    return result

