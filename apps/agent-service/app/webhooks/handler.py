"""
Recoup — Razorpay Webhook Handler.

Receives Razorpay webhook events, verifies HMAC-SHA256 signatures,
enforces idempotency, converts payload format, and dispatches to agent pipeline.
"""

import json
import logging
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Header, Response

from app.webhooks.signature import verify_razorpay_signature
from app.webhooks.idempotency import is_event_processed, record_idempotency_key
from app.graph.pipeline import process_event

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/razorpay")
async def handle_razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None),
):
    """
    Razorpay Webhook Endpoint.

    Supported Webhook Events:
    - payment.failed
    - payment.captured / payment_link.paid
    - subscription.charged / subscription.halted
    """
    raw_body = await request.body()

    # Step 1: Verify HMAC Signature
    if x_razorpay_signature and not verify_razorpay_signature(raw_body, x_razorpay_signature):
        logger.warning("Invalid Razorpay webhook signature")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    # Step 2: Parse Body JSON
    try:
        payload = json.loads(raw_body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

    rzp_event = payload.get("event", "")
    event_id = payload.get("event_id", payload.get("contains", [""])[0] if "contains" in payload else "")

    # Extract payment entity
    payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    payment_id = payment_entity.get("id", "")
    idempotency_key = event_id or payment_id or f"rzp_evt_{hash(raw_body)}"

    # Step 3: Check Idempotency (Duplicate Prevention)
    is_duplicate, prev_result = await is_event_processed(idempotency_key)
    if is_duplicate:
        logger.info(f"Safely ignoring duplicate webhook event: {idempotency_key}")
        return {
            "status": "ignored",
            "reason": "duplicate_webhook",
            "idempotency_key": idempotency_key,
            "previous_result": prev_result,
        }

    # Step 4: Convert Razorpay payload format to Recoup internal Event
    recoup_event = _convert_razorpay_payload(rzp_event, payload)
    if not recoup_event:
        return {"status": "ignored", "reason": f"unhandled_event_type_{rzp_event}"}

    # Step 5: Process through Agent Graph Pipeline
    case_result = process_event(recoup_event)

    # Step 6: Store Idempotency Key
    await record_idempotency_key(
        idempotency_key=idempotency_key,
        event_id=recoup_event["event_id"],
        result={
            "case_id": case_result["case_id"],
            "case_status": case_result["case_status"],
            "root_cause": case_result.get("root_cause", ""),
        },
    )

    return {
        "status": "processed",
        "case_id": case_result["case_id"],
        "event_type": case_result["event_type"],
        "case_status": case_result["case_status"],
        "root_cause": case_result.get("root_cause", ""),
    }


def _convert_razorpay_payload(rzp_event: str, payload: dict) -> Optional[dict]:
    """Convert raw Razorpay webhook payload into Recoup internal event schema."""
    payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    order_entity = payload.get("payload", {}).get("order", {}).get("entity", {})
    subscription_entity = payload.get("payload", {}).get("subscription", {}).get("entity", {})

    amount_inr = (payment_entity.get("amount", 0) or order_entity.get("amount", 0)) / 100.0
    decline_reason = payment_entity.get("error_description", payment_entity.get("error_reason", "Payment failed"))
    decline_code = payment_entity.get("error_code", "")

    customer_email = payment_entity.get("email", "")
    customer_phone = payment_entity.get("contact", "")
    customer_name = payment_entity.get("notes", {}).get("customer_name", "Valued Customer")

    if rzp_event in ("payment.failed", "payment_link.cancelled"):
        return {
            "event_id": payload.get("event_id", f"evt_rzp_{payment_entity.get('id', '')}"),
            "event_type": "payment_failed",
            "payment_id": payment_entity.get("id", ""),
            "order_id": payment_entity.get("order_id", ""),
            "amount": amount_inr,
            "currency": payment_entity.get("currency", "INR"),
            "decline_reason": decline_reason,
            "decline_code": decline_code,
            "method": payment_entity.get("method", "card"),
            "bank": payment_entity.get("bank", "Bank"),
            "customer": {
                "id": payment_entity.get("customer_id", f"cust_{customer_email[:8]}"),
                "email": customer_email,
                "phone": customer_phone,
                "name": customer_name,
            },
            "timestamp": payload.get("created_at", ""),
        }

    elif rzp_event in ("subscription.halted", "subscription.charged"):
        return {
            "event_id": payload.get("event_id", f"evt_sub_{subscription_entity.get('id', '')}"),
            "event_type": "mandate_failed",
            "subscription_id": subscription_entity.get("id", ""),
            "plan_id": subscription_entity.get("plan_id", ""),
            "amount": (subscription_entity.get("quantity", 1) * subscription_entity.get("paid_count", 1) * 100),
            "currency": "INR",
            "attempt_number": subscription_entity.get("paid_count", 1) + 1,
            "days_overdue": 1,
            "mandate_type": "emandate",
            "failure_reason": "Subscription mandate charge failed",
            "customer": {
                "id": subscription_entity.get("customer_id", "cust_sub"),
                "email": customer_email,
                "phone": customer_phone,
                "name": customer_name,
            },
            "timestamp": payload.get("created_at", ""),
        }

    return None
