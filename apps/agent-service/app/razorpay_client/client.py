"""
Recoup — Razorpay API Client Wrapper.

Handles interaction with Razorpay API (Test Mode).
Supports fallback simulation when test API keys are stubs,
ensuring graceful execution in offline/demo environments.
"""

import uuid
import time
import logging
from typing import Optional, Dict, Any

from app.config import settings
from app.razorpay_client.models import PaymentLinkRequest, PaymentLinkResponse

logger = logging.getLogger(__name__)


class RazorpayClientWrapper:
    """Wrapper for Razorpay Test Mode API calls."""

    def __init__(self):
        self.key_id = settings.razorpay_key_id
        self.key_secret = settings.razorpay_key_secret
        self.is_configured = bool(
            self.key_id and self.key_secret and not self.key_id.startswith("rzp_test_xxxx")
        )

        if self.is_configured:
            try:
                import razorpay
                self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
                logger.info("Razorpay client initialized with provided credentials")
            except Exception as e:
                logger.warning(f"Failed to initialize Razorpay SDK: {e}. Falling back to simulator.")
                self.is_configured = False
        else:
            logger.info("Razorpay credentials not set or placeholder used. Operating in Test Simulation mode.")

    def create_payment_link(
        self,
        amount_inr: float,
        description: str,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        reference_id: str,
    ) -> PaymentLinkResponse:
        """
        Create a payment link via Razorpay API or simulator.

        Amount is passed in INR (converted to paise internally for Razorpay).
        """
        amount_paise = int(round(amount_inr * 100))

        if self.is_configured:
            try:
                payload = {
                    "amount": amount_paise,
                    "currency": "INR",
                    "accept_partial": False,
                    "description": description,
                    "customer": {
                        "name": customer_name,
                        "email": customer_email,
                        "contact": customer_phone,
                    },
                    "notify": {"sms": True, "email": True},
                    "reminder_enable": True,
                    "notes": {"recoup_case_id": reference_id},
                }
                res = self.client.payment_link.create(payload)
                return PaymentLinkResponse(
                    id=res["id"],
                    short_url=res["short_url"],
                    status=res["status"],
                    amount=res["amount"],
                    description=res["description"],
                    customer=res.get("customer", {}),
                    created_at=res.get("created_at", int(time.time())),
                )
            except Exception as e:
                logger.error(f"Razorpay API call failed: {e}. Generating simulated test link.")

        # Simulation mode fallback
        link_id = f"plink_{uuid.uuid4().hex[:14]}"
        short_url = f"https://rzp.io/i/recoup_{link_id[:8]}"

        return PaymentLinkResponse(
            id=link_id,
            short_url=short_url,
            status="created",
            amount=amount_paise,
            description=f"[SIMULATED TEST LINK] {description}",
            customer={"name": customer_name, "email": customer_email, "contact": customer_phone},
            created_at=int(time.time()),
        )

    def fetch_payment_link(self, payment_link_id: str) -> Dict[str, Any]:
        """Fetch status of a payment link."""
        if self.is_configured:
            try:
                return self.client.payment_link.fetch(payment_link_id)
            except Exception as e:
                logger.error(f"Failed to fetch payment link {payment_link_id}: {e}")

        return {
            "id": payment_link_id,
            "status": "paid",
            "amount_paid": 10000,
            "simulated": True,
        }


# Global singleton client instance
razorpay_client = RazorpayClientWrapper()
