"""
Recoup — Webhook Signature Verification.

Validates Razorpay HMAC-SHA256 signatures for incoming webhooks.
Uses constant-time comparison to prevent timing attacks.
"""

import hmac
import hashlib
import logging
from app.config import settings

logger = logging.getLogger(__name__)


def verify_razorpay_signature(raw_body: bytes, signature: str, secret: str = "") -> bool:
    """
    Verify Razorpay webhook HMAC-SHA256 signature.

    Args:
        raw_body: The raw request body as bytes.
        signature: The signature string from 'x-razorpay-signature' header.
        secret: Optional webhook secret override. Uses settings if not provided.

    Returns:
        bool: True if signature matches, False otherwise.
    """
    webhook_secret = secret or settings.razorpay_webhook_secret

    # If no secret configured in test/demo mode, allow request with warning
    if not webhook_secret or webhook_secret == "your_webhook_secret_here":
        logger.warning("Razorpay webhook secret not set in .env. Skipping HMAC verification for test mode.")
        return True

    if not signature:
        return False

    try:
        expected_signature = hmac.new(
            key=webhook_secret.encode("utf-8"),
            msg=raw_body,
            digestmod=hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False
