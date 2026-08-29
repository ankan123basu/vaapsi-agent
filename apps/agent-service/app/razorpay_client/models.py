"""
Recoup — Razorpay Response Models.

Pydantic models for Razorpay API requests and responses.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class PaymentLinkRequest(BaseModel):
    """Request model for creating a Razorpay Payment Link."""
    amount: int = Field(description="Amount in paise (e.g. 10000 = ₹100.00)")
    currency: str = "INR"
    accept_partial: bool = False
    description: str
    customer: Dict[str, str] = Field(description="name, email, contact")
    notify: Dict[str, bool] = Field(default_factory=lambda: {"sms": True, "email": True})
    reminder_enable: bool = True
    notes: Dict[str, str] = Field(default_factory=dict)
    callback_url: Optional[str] = None
    callback_method: str = "get"


class PaymentLinkResponse(BaseModel):
    """Response model for a created Razorpay Payment Link."""
    id: str
    short_url: str
    status: str
    amount: int
    amount_paid: int = 0
    currency: str = "INR"
    description: str
    customer: Dict[str, Any] = Field(default_factory=dict)
    created_at: int
