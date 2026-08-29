# ADR-0002: Idempotent Webhook Handling & Out-of-Order Safety

**Status:** Accepted  
**Date:** 2026-08-28  
**Context:** Payment gateways (such as Razorpay) retry webhooks upon network timeouts, backpressure, or delivery glitches. Out-of-order deliveries and duplicate webhooks are guaranteed occurrences in production payment systems.

If the Recoup agent processes a duplicate `payment.failed` event or receives an out-of-order webhook after a case has already been resolved or blocked, naive processing could trigger redundant recovery messages, spam customers, or regress the internal case state.

## Decision

### 1. Unique Idempotency Keying
- Every incoming webhook is checked against an `idempotency_keys` table using `(event_id || payment_id)`.
- If a matching key is found in the store:
  - The webhook execution immediately short-circuits.
  - Returns HTTP 200 OK with `{"status": "ignored", "reason": "duplicate_webhook"}`.
  - A safe no-op entry is logged to the immutable audit trail.

### 2. Forward-Only State Machine
- Case state transitions follow a strict directed acyclic graph (DAG):
  `detected → diagnosed → strategy_set → guardrail_checked → executing → executed → (recovered | failed | blocked)`.
- Terminal states (`recovered`, `blocked`, `failed`) are immutable. Once a case reaches a terminal state, incoming events for that payment ID cannot regress its status.

### 3. Constant-Time Signature Verification
- Webhook signature verification uses HMAC-SHA256 with `hmac.compare_digest` to prevent timing side-channel attacks.

## Consequences
- Eliminates customer spam from duplicate webhook retries.
- Guarantees exact-once recovery execution.
- Enables safe replay of webhook streams in evaluation and testing.
