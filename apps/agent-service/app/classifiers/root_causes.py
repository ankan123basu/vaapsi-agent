"""
Recoup — Root Cause Categories.

Enumeration of all root-cause categories the Diagnoser can assign.
Shared by both the rules engine and the LLM classifier.
"""

from enum import Enum


class RootCause(str, Enum):
    """Root-cause categories for revenue leakage."""

    # Payment failure causes
    INSUFFICIENT_FUNDS = "insufficient_funds"
    EXPIRED_INSTRUMENT = "expired_instrument"
    ISSUER_UNAVAILABLE = "issuer_unavailable"
    RISK_DECLINED = "risk_declined"
    AUTHENTICATION_FAILED = "authentication_failed"
    INVALID_DETAILS = "invalid_details"
    NETWORK_ERROR = "network_error"
    LIMIT_EXCEEDED = "limit_exceeded"

    # Customer-action causes
    CUSTOMER_ACTION_NEEDED = "customer_action_needed"

    # Mandate-specific causes
    MANDATE_ISSUE = "mandate_issue"

    # Checkout-specific causes
    CHECKOUT_FRICTION = "checkout_friction"
    PRICE_SENSITIVITY = "price_sensitivity"
    COMPARISON_SHOPPING = "comparison_shopping"

    # Fallback
    UNKNOWN = "unknown"


# Human-readable descriptions for the dashboard
ROOT_CAUSE_DESCRIPTIONS: dict[str, str] = {
    "insufficient_funds": "Customer's account has insufficient funds",
    "expired_instrument": "Payment instrument (card/mandate) has expired",
    "issuer_unavailable": "Issuing bank or gateway is temporarily down",
    "risk_declined": "Transaction declined by fraud/risk detection system",
    "authentication_failed": "3DS/OTP authentication failed or timed out",
    "invalid_details": "Incorrect card number, CVV, PIN, or UPI VPA",
    "network_error": "Network or gateway connectivity issue",
    "limit_exceeded": "Transaction exceeds card/account limits",
    "customer_action_needed": "Customer needs to take action (update card, contact bank)",
    "mandate_issue": "Subscription mandate not approved, revoked, or failed to debit",
    "checkout_friction": "Checkout flow was too long or confusing",
    "price_sensitivity": "Customer likely abandoned due to price",
    "comparison_shopping": "Customer likely comparing across sites",
    "unknown": "Unable to determine root cause with confidence",
}


# Which root causes are retryable (automatic retry makes sense)
RETRYABLE_ROOT_CAUSES = {
    RootCause.INSUFFICIENT_FUNDS,
    RootCause.ISSUER_UNAVAILABLE,
    RootCause.AUTHENTICATION_FAILED,
    RootCause.INVALID_DETAILS,
    RootCause.NETWORK_ERROR,
    RootCause.CHECKOUT_FRICTION,
    RootCause.MANDATE_ISSUE,
}

# Which root causes need a different payment method
NEEDS_NEW_INSTRUMENT = {
    RootCause.EXPIRED_INSTRUMENT,
    RootCause.LIMIT_EXCEEDED,
    RootCause.RISK_DECLINED,
}
