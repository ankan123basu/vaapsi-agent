"""
Recoup — Webhook Verification & Idempotency Proof Script.

Proves:
1. Raw HMAC-SHA256 signature verification works.
2. Invalid signatures are rejected with 400 Bad Request.
3. Valid webhook payloads are processed.
4. Duplicate webhook delivery (same event_id) is SAFELY NO-OP'd (status: ignored, reason: duplicate_webhook).
"""

import uuid
import sys
import os
import json
import hmac
import hashlib
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings
from app.database import init_db


WEBHOOK_SECRET = "test_webhook_secret_99"


def generate_signature(raw_body: bytes, secret: str) -> str:
    return hmac.new(
        key=secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()


async def run_webhook_proof():
    await init_db()

    # Set secret override for test
    settings.razorpay_webhook_secret = WEBHOOK_SECRET

    payload = {
        "entity": "event",
        "account_id": "acc_111111",
        "event": "payment.failed",
        "contains": ["payment"],
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_proof_999888",
                    "entity": "payment",
                    "amount": 250000, # ₹2,500.00
                    "currency": "INR",
                    "status": "failed",
                    "order_id": "order_proof_111",
                    "method": "card",
                    "bank": "HDFC",
                    "error_code": "BAD_REQUEST_ERROR",
                    "error_description": "Card expired",
                    "email": "proof.customer@example.com",
                    "contact": "+919876543210",
                    "notes": {"customer_name": "Rohan Proof"}
                }
            }
        },
        "created_at": 1740000000,
        "event_id": f"evt_proof_{uuid.uuid4().hex[:8]}"
    }

    raw_body = json.dumps(payload, separators=(',', ':')).encode("utf-8")
    valid_sig = generate_signature(raw_body, WEBHOOK_SECRET)
    invalid_sig = "invalid_signature_12345"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        print("=" * 60)
        print("WEBHOOK INTEGRATION & IDEMPOTENCY PROOF")
        print("=" * 60)

        # 1. Invalid Signature Test
        print("\n1. Testing Invalid Signature:")
        res1 = await client.post(
            "/webhooks/razorpay",
            content=raw_body,
            headers={"x-razorpay-signature": invalid_sig, "content-type": "application/json"}
        )
        print(f"   HTTP Status: {res1.status_code}")
        print(f"   Response:    {res1.json()}")
        sig_rejected = res1.status_code == 400

        # 2. First Valid Payload Delivery
        print("\n2. Delivering Webhook Event (1st time):")
        res2 = await client.post(
            "/webhooks/razorpay",
            content=raw_body,
            headers={"x-razorpay-signature": valid_sig, "content-type": "application/json"}
        )
        print(f"   HTTP Status: {res2.status_code}")
        print(f"   Response:    {json.dumps(res2.json(), indent=2)}")
        first_processed = res2.status_code == 200 and res2.json().get("status") == "processed"

        # 3. Duplicate Delivery (Replay attack simulation)
        print("\n3. Delivering REPLAY Webhook Event (2nd time with SAME event_id):")
        res3 = await client.post(
            "/webhooks/razorpay",
            content=raw_body,
            headers={"x-razorpay-signature": valid_sig, "content-type": "application/json"}
        )
        print(f"   HTTP Status: {res3.status_code}")
        print(f"   Response:    {json.dumps(res3.json(), indent=2)}")
        second_ignored = res3.status_code == 200 and res3.json().get("status") == "ignored"

        print("\n" + "=" * 60)
        print("SUMMARY OF PROOF")
        print("=" * 60)
        print(f"  Invalid Signature Rejected (400 Bad Request): {'PASS' if sig_rejected else 'FAIL'}")
        print(f"  First Webhook Processed (200 OK):             {'PASS' if first_processed else 'FAIL'}")
        print(f"  Duplicate Webhook Ignored/No-op (Idempotent): {'PASS' if second_ignored else 'FAIL'}")
        print()


if __name__ == "__main__":
    asyncio.run(run_webhook_proof())
