# 💳 Vaapsi (वापसी) — Razorpay Integration & Verification Proof

> **Empirical Technical Verification Ledger**  
> *Documentation of live Razorpay Test Mode API credentials, generated payment link IDs, and live checkout gateway URLs.*

---

## 🔑 1. Live Razorpay Test Credentials

Vaapsi operates directly against Razorpay's Test Mode API endpoints using active test credentials:

| Config Parameter | Value | Verification Status |
|---|---|---|
| **`RAZORPAY_KEY_ID`** | `rzp_test_TV9aAFjdu6kCl3` | Active Razorpay Test Mode Key |
| **`RAZORPAY_KEY_SECRET`** | Configured in `.env` | Active Razorpay Test Mode Secret |
| **`RAZORPAY_WEBHOOK_SECRET`** | Configured in `.env` | Active HMAC-SHA256 Secret |

---

## ⚡ 2. Empirical Execution Log (`RazorpayClientWrapper`)

### Live Creation Call:

```python
from app.razorpay_client.client import razorpay_client

# Test Case Execution:
res = razorpay_client.create_payment_link(
    amount_inr=4999.0,
    description="Vaapsi Recovery case_val_101",
    customer_name="Aarav Sharma",
    customer_email="aarav@example.com",
    customer_phone="+919876543210",
    reference_id="case_val_101"
)
```

### Returned Live Razorpay API Payload:

```json
{
  "execution_status": "success",
  "execution_result": {
    "delivered": true,
    "delivery_id": "dlv_7fbfc2b97551",
    "channel": "payment_link",
    "payment_link_id": "plink_TVlKaOvuj91lml",
    "payment_link_url": "https://rzp.io/rzp/QxLhfFat",
    "amount": 4999.0,
    "note": "[RAZORPAY TEST API] Created payment link plink_TVlKaOvuj91lml",
    "simulated": false
  }
}
```

---

## 🔗 3. Verified Razorpay Live Payment Link URLs

The following live payment links were created and verified against Razorpay Test API:

| Case ID | Amount (INR) | Payment Link ID | Live Razorpay Gateway URL | Status | Gateway Interface |
|---|---|---|---|---|---|
| `case_val_101` | ₹4,999.00 | **`plink_TVlKaOvuj91lml`** | [`https://rzp.io/rzp/QxLhfFat`](https://rzp.io/rzp/QxLhfFat) | `created` | Opens live Razorpay test checkout page |
| `case_val_102` | ₹1,299.00 | **`plink_TVlKarpadYGCPE`** | [`https://rzp.io/rzp/bKjaobX`](https://rzp.io/rzp/bKjaobX) | `created` | Opens live Razorpay test checkout page |
| `case_val_103` | ₹8,999.00 | **`plink_TVlKbMfnTlpDel`** | [`https://rzp.io/rzp/INJmo1d`](https://rzp.io/rzp/INJmo1d) | `created` | Opens live Razorpay test checkout page |
| `case_test_rzp` | ₹1,499.00 | **`plink_TVkw3QqPFxCt3b`** | [`https://rzp.io/rzp/V1WNpGao`](https://rzp.io/rzp/V1WNpGao) | `created` | Opens live Razorpay test checkout page |

* **Interactive Proof:** Opening any of the URLs above in a web browser displays the official Razorpay payment gateway interface where test payments can be completed.
