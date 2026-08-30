"""
Recoup — Webhook & Idempotency Integration Tests.
"""

import pytest
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.webhooks.signature import verify_razorpay_signature
from app.webhooks.idempotency import is_event_processed, record_idempotency_key
from app.webhooks.handler import _convert_razorpay_payload


def test_signature_verification():
    """Test HMAC-SHA256 signature verification logic."""
    raw_body = b'{"event":"payment.failed"}'
    secret = "test_secret_123"

    import hmac
    import hashlib
    valid_sig = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    assert verify_razorpay_signature(raw_body, valid_sig, secret) is True
    assert verify_razorpay_signature(raw_body, "invalid_signature", secret) is False


def test_payload_conversion():
    """Test converting Razorpay webhook payload to Recoup internal event schema."""
    rzp_payload = {
        "event": "payment.failed",
        "event_id": "evt_rzp_999",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_999",
                    "amount": 500000,
                    "currency": "INR",
                    "error_description": "Card has expired",
                    "error_code": "EXPIRED_CARD",
                    "method": "card",
                    "bank": "HDFC Bank",
                    "email": "test@example.com",
                    "contact": "+919876543210",
                }
            }
        }
    }

    event = _convert_razorpay_payload("payment.failed", rzp_payload)

    assert event is not None
    assert event["event_type"] == "payment_failed"
    assert event["amount"] == 5000.0
    assert event["decline_code"] == "EXPIRED_CARD"
    assert event["customer"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_idempotency_recording():
    """Test recording and checking idempotency keys."""
    import uuid
    from app.database import init_db
    await init_db()

    key = f"test_key_unique_{uuid.uuid4().hex[:8]}"
    event_id = f"evt_test_{uuid.uuid4().hex[:8]}"

    is_dup, _ = await is_event_processed(key)
    assert is_dup is False

    rec_ok = await record_idempotency_key(key, event_id, {"status": "processed", "case_id": "case_123"})
    assert rec_ok is True

    is_dup_after, prev_res = await is_event_processed(key)
    assert is_dup_after is True
    assert prev_res["case_id"] == "case_123"


if __name__ == "__main__":
    print("\n=== Running Webhook & Idempotency Tests ===\n")
    test_signature_verification()
    print("  [OK] Signature verification test passed")
    test_payload_conversion()
    print("  [OK] Payload conversion test passed")

    asyncio.run(test_idempotency_recording())
    print("  [OK] Idempotency recording test passed")
    print("\n=== All Webhook Tests Passed! ===\n")
