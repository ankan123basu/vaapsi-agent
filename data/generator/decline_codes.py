"""
Recoup — Decline Code Taxonomy.

Realistic bank/gateway decline codes with root-cause mappings.
This is the deterministic layer of the Diagnoser — no LLM needed for these.
"""

from enum import Enum
from typing import NamedTuple


class RootCause(str, Enum):
    """Root-cause categories for payment failures."""
    INSUFFICIENT_FUNDS = "insufficient_funds"
    EXPIRED_INSTRUMENT = "expired_instrument"
    ISSUER_UNAVAILABLE = "issuer_unavailable"
    RISK_DECLINED = "risk_declined"
    AUTHENTICATION_FAILED = "authentication_failed"
    INVALID_DETAILS = "invalid_details"
    NETWORK_ERROR = "network_error"
    LIMIT_EXCEEDED = "limit_exceeded"
    CUSTOMER_ACTION_NEEDED = "customer_action_needed"
    MANDATE_ISSUE = "mandate_issue"
    CHECKOUT_FRICTION = "checkout_friction"
    UNKNOWN = "unknown"


class DeclineCodeMapping(NamedTuple):
    """Mapping from a decline code to its root cause."""
    code: str
    description: str
    root_cause: RootCause
    is_retryable: bool
    suggested_channel: str  # preferred recovery channel
    urgency: str  # "high", "medium", "low"


# ============================================
# DETERMINISTIC DECLINE CODE → ROOT CAUSE MAP
# ============================================
# This is the rules layer of the Diagnoser.
# If a decline code matches here, NO LLM call is needed.
# ============================================

DECLINE_CODE_MAP: dict[str, DeclineCodeMapping] = {
    # --- Insufficient Funds ---
    "INSUFFICIENT_FUNDS": DeclineCodeMapping(
        code="INSUFFICIENT_FUNDS",
        description="Card has insufficient funds to complete the transaction",
        root_cause=RootCause.INSUFFICIENT_FUNDS,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="medium",
    ),
    "NSF": DeclineCodeMapping(
        code="NSF",
        description="Non-sufficient funds",
        root_cause=RootCause.INSUFFICIENT_FUNDS,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="medium",
    ),
    "BALANCE_INSUFFICIENT": DeclineCodeMapping(
        code="BALANCE_INSUFFICIENT",
        description="Account balance insufficient",
        root_cause=RootCause.INSUFFICIENT_FUNDS,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="medium",
    ),

    # --- Expired Instrument ---
    "EXPIRED_CARD": DeclineCodeMapping(
        code="EXPIRED_CARD",
        description="Card has expired",
        root_cause=RootCause.EXPIRED_INSTRUMENT,
        is_retryable=False,
        suggested_channel="email",
        urgency="high",
    ),
    "CARD_EXPIRED": DeclineCodeMapping(
        code="CARD_EXPIRED",
        description="The card used is expired",
        root_cause=RootCause.EXPIRED_INSTRUMENT,
        is_retryable=False,
        suggested_channel="email",
        urgency="high",
    ),
    "INVALID_EXPIRY": DeclineCodeMapping(
        code="INVALID_EXPIRY",
        description="Invalid expiry date provided",
        root_cause=RootCause.EXPIRED_INSTRUMENT,
        is_retryable=False,
        suggested_channel="email",
        urgency="high",
    ),

    # --- Issuer Unavailable ---
    "ISSUER_UNAVAILABLE": DeclineCodeMapping(
        code="ISSUER_UNAVAILABLE",
        description="Card issuer bank is temporarily unavailable",
        root_cause=RootCause.ISSUER_UNAVAILABLE,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="low",
    ),
    "BANK_DOWN": DeclineCodeMapping(
        code="BANK_DOWN",
        description="Issuing bank systems are down",
        root_cause=RootCause.ISSUER_UNAVAILABLE,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="low",
    ),
    "ISSUER_NOT_AVAILABLE": DeclineCodeMapping(
        code="ISSUER_NOT_AVAILABLE",
        description="Issuer is not available for authorization",
        root_cause=RootCause.ISSUER_UNAVAILABLE,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="low",
    ),
    "BANK_TIMEOUT": DeclineCodeMapping(
        code="BANK_TIMEOUT",
        description="Bank did not respond in time",
        root_cause=RootCause.ISSUER_UNAVAILABLE,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="low",
    ),

    # --- Risk Declined ---
    "RISK_DECLINED": DeclineCodeMapping(
        code="RISK_DECLINED",
        description="Transaction declined by risk/fraud detection system",
        root_cause=RootCause.RISK_DECLINED,
        is_retryable=False,
        suggested_channel="email",
        urgency="high",
    ),
    "FRAUD_SUSPECTED": DeclineCodeMapping(
        code="FRAUD_SUSPECTED",
        description="Suspected fraudulent transaction",
        root_cause=RootCause.RISK_DECLINED,
        is_retryable=False,
        suggested_channel="email",
        urgency="high",
    ),
    "SECURITY_VIOLATION": DeclineCodeMapping(
        code="SECURITY_VIOLATION",
        description="Transaction flagged for security violation",
        root_cause=RootCause.RISK_DECLINED,
        is_retryable=False,
        suggested_channel="email",
        urgency="high",
    ),
    "RESTRICTED_CARD": DeclineCodeMapping(
        code="RESTRICTED_CARD",
        description="Card is restricted from this type of transaction",
        root_cause=RootCause.RISK_DECLINED,
        is_retryable=False,
        suggested_channel="email",
        urgency="medium",
    ),

    # --- Authentication Failed ---
    "3DS_TIMEOUT": DeclineCodeMapping(
        code="3DS_TIMEOUT",
        description="3D Secure authentication timed out",
        root_cause=RootCause.AUTHENTICATION_FAILED,
        is_retryable=True,
        suggested_channel="sms",
        urgency="high",
    ),
    "OTP_TIMEOUT": DeclineCodeMapping(
        code="OTP_TIMEOUT",
        description="OTP entry timed out",
        root_cause=RootCause.AUTHENTICATION_FAILED,
        is_retryable=True,
        suggested_channel="sms",
        urgency="high",
    ),
    "3DS_FAILED": DeclineCodeMapping(
        code="3DS_FAILED",
        description="3D Secure authentication failed",
        root_cause=RootCause.AUTHENTICATION_FAILED,
        is_retryable=True,
        suggested_channel="sms",
        urgency="high",
    ),
    "OTP_INCORRECT": DeclineCodeMapping(
        code="OTP_INCORRECT",
        description="Incorrect OTP entered",
        root_cause=RootCause.AUTHENTICATION_FAILED,
        is_retryable=True,
        suggested_channel="sms",
        urgency="high",
    ),
    "AUTHENTICATION_REQUIRED": DeclineCodeMapping(
        code="AUTHENTICATION_REQUIRED",
        description="Additional authentication required",
        root_cause=RootCause.AUTHENTICATION_FAILED,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="medium",
    ),

    # --- Invalid Details ---
    "INVALID_CVV": DeclineCodeMapping(
        code="INVALID_CVV",
        description="Invalid CVV provided",
        root_cause=RootCause.INVALID_DETAILS,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="high",
    ),
    "INVALID_CARD_NUMBER": DeclineCodeMapping(
        code="INVALID_CARD_NUMBER",
        description="Invalid card number",
        root_cause=RootCause.INVALID_DETAILS,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="high",
    ),
    "INVALID_PIN": DeclineCodeMapping(
        code="INVALID_PIN",
        description="Incorrect PIN entered",
        root_cause=RootCause.INVALID_DETAILS,
        is_retryable=True,
        suggested_channel="sms",
        urgency="high",
    ),
    "INVALID_VPA": DeclineCodeMapping(
        code="INVALID_VPA",
        description="Invalid UPI VPA",
        root_cause=RootCause.INVALID_DETAILS,
        is_retryable=True,
        suggested_channel="sms",
        urgency="medium",
    ),

    # --- Network Error ---
    "NETWORK_ERROR": DeclineCodeMapping(
        code="NETWORK_ERROR",
        description="Network connectivity issue during transaction",
        root_cause=RootCause.NETWORK_ERROR,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="low",
    ),
    "GATEWAY_ERROR": DeclineCodeMapping(
        code="GATEWAY_ERROR",
        description="Payment gateway encountered an error",
        root_cause=RootCause.NETWORK_ERROR,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="low",
    ),
    "TIMEOUT": DeclineCodeMapping(
        code="TIMEOUT",
        description="Transaction timed out",
        root_cause=RootCause.NETWORK_ERROR,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="low",
    ),

    # --- Limit Exceeded ---
    "LIMIT_EXCEEDED": DeclineCodeMapping(
        code="LIMIT_EXCEEDED",
        description="Transaction exceeds card/account limit",
        root_cause=RootCause.LIMIT_EXCEEDED,
        is_retryable=False,
        suggested_channel="email",
        urgency="medium",
    ),
    "DAILY_LIMIT_REACHED": DeclineCodeMapping(
        code="DAILY_LIMIT_REACHED",
        description="Daily transaction limit reached",
        root_cause=RootCause.LIMIT_EXCEEDED,
        is_retryable=True,
        suggested_channel="payment_link",
        urgency="low",
    ),
    "CARD_BLOCKED": DeclineCodeMapping(
        code="CARD_BLOCKED",
        description="Card has been blocked by the issuer",
        root_cause=RootCause.LIMIT_EXCEEDED,
        is_retryable=False,
        suggested_channel="email",
        urgency="high",
    ),

    # --- Mandate-Specific ---
    "MANDATE_NOT_APPROVED": DeclineCodeMapping(
        code="MANDATE_NOT_APPROVED",
        description="e-Mandate/NACH not approved by customer",
        root_cause=RootCause.MANDATE_ISSUE,
        is_retryable=True,
        suggested_channel="email",
        urgency="high",
    ),
    "MANDATE_REVOKED": DeclineCodeMapping(
        code="MANDATE_REVOKED",
        description="Customer revoked the mandate",
        root_cause=RootCause.MANDATE_ISSUE,
        is_retryable=False,
        suggested_channel="email",
        urgency="high",
    ),
    "DEBIT_FAILED": DeclineCodeMapping(
        code="DEBIT_FAILED",
        description="Debit against mandate failed",
        root_cause=RootCause.MANDATE_ISSUE,
        is_retryable=True,
        suggested_channel="sms",
        urgency="medium",
    ),
}

# List of all known decline codes for quick lookup
KNOWN_DECLINE_CODES = set(DECLINE_CODE_MAP.keys())

# Ambiguous decline reasons that should go to the LLM fallback
AMBIGUOUS_DECLINE_REASONS = [
    "DO_NOT_HONOR",
    "GENERAL_DECLINE",
    "DECLINE",
    "PROCESSING_ERROR",
    "SYSTEM_ERROR",
    "UNKNOWN_ERROR",
    "CONTACT_BANK",
    "REFER_TO_ISSUER",
    "TRY_AGAIN",
    "NOT_PERMITTED",
    "SERVICE_NOT_ALLOWED",
]
