"""
Recoup — RecoveryCase State Definition.

The typed state object that flows through the entire LangGraph pipeline.
Every node reads from and writes to this shared state — this IS the audit trail.
"""

from typing import TypedDict, Optional, Annotated
from enum import Enum
import operator


class CaseStatus(str, Enum):
    """Forward-only state machine for recovery cases."""
    DETECTED = "detected"
    DIAGNOSED = "diagnosed"
    SUPPRESSED = "suppressed"  # Nuisance-suppression: likely self-resolving
    STRATEGY_SET = "strategy_set"
    GUARDRAIL_CHECKED = "guardrail_checked"
    EXECUTING = "executing"
    EXECUTED = "executed"
    RECOVERED = "recovered"
    FAILED = "failed"
    BLOCKED = "blocked"
    PENDING_APPROVAL = "pending_approval"


# Valid state transitions — forward only, never backward
VALID_TRANSITIONS: dict[str, set[str]] = {
    "detected": {"diagnosed"},
    "diagnosed": {"strategy_set", "suppressed"},
    "suppressed": set(),    # terminal state — monitored, no contact
    "strategy_set": {"guardrail_checked"},
    "guardrail_checked": {"executing", "blocked", "pending_approval"},
    "pending_approval": {"executing", "blocked"},
    "executing": {"executed", "failed"},
    "executed": {"recovered", "failed"},
    "recovered": set(),  # terminal state
    "failed": set(),     # terminal state
    "blocked": set(),    # terminal state
}


def can_transition(current: str, target: str) -> bool:
    """Check if a state transition is valid (forward-only)."""
    return target in VALID_TRANSITIONS.get(current, set())


class AuditEntry(TypedDict):
    """A single entry in the audit trail."""
    node_name: str
    input_summary: str
    output_summary: str
    reasoning: str
    provider: str
    latency_ms: float
    timestamp: str


class RecoveryCase(TypedDict, total=False):
    """
    The shared state object for the LangGraph recovery pipeline.

    Every node reads from and writes to this state.
    The full state IS the audit trail — fully inspectable end to end.
    """
    # --- Identity ---
    case_id: str
    event_id: str
    event_type: str  # payment_failed | checkout_abandoned | mandate_failed
    raw_event: dict

    # --- Customer ---
    customer_id: str
    customer_email: str
    customer_phone: str
    customer_name: str
    customer_opted_out: bool

    # --- Financial ---
    amount_at_risk: float
    currency: str

    # --- Detector output ---
    detected_at: str
    decline_reason_raw: str

    # --- Diagnoser output ---
    root_cause: str
    root_cause_confidence: float
    diagnosis_method: str  # "rule" | "llm_fallback"
    diagnosis_reasoning: str
    diagnosis_provider: str  # e.g. "groq/llama-3.3-70b" or "gemini/gemini-2.0-flash"
    diagnosis_latency_ms: float

    # --- Strategist output ---
    recovery_channel: str  # email | sms | whatsapp | voice | payment_link
    recovery_action: str
    message_content: str
    offer_details: dict
    scheduled_at: str

    # --- Guardrail Gate output ---
    guardrail_status: str  # approved | blocked | needs_human_approval
    guardrail_violations: list[str]

    # --- Executor output ---
    execution_status: str
    execution_result: dict
    razorpay_payment_link_id: str

    # --- Reporter output ---
    recovery_amount: float

    # --- Nuisance-Suppression Scorer output ---
    self_resolution_probability: float
    contact_suppressed: bool
    suppression_reasoning: str

    # --- Case lifecycle ---
    case_status: str
    retry_count: int
    idempotency_key: str

    # --- Audit trail (append-only) ---
    audit_trail: Annotated[list[dict], operator.add]

    # --- Timestamps ---
    created_at: str
    updated_at: str
