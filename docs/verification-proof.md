# 💳 Vaapsi (वापसी) — Razorpay Integration & Verification Proof

> **Empirical Technical Verification Ledger**  
> *Documentation of live Razorpay Test Mode API credentials, generated payment link IDs, and live checkout gateway URLs.*

---

## 🔑 1. Live Razorpay Test Credentials

Vaapsi operates directly against Razorpay's Test Mode API endpoints using configured test credentials:

| Config Parameter | Value | Verification Status |
|---|---|---|
| **`RAZORPAY_KEY_ID`** | `rzp_test_TV9aAFjdu6kCl3` | Active Razorpay Test Mode Key |
| **`RAZORPAY_KEY_SECRET`** | Configured in `.env` | Active Razorpay Test Mode Secret |
| **`RAZORPAY_WEBHOOK_SECRET`** | Configured in `.env` | Active HMAC-SHA256 Secret |

---

## ⚡ 2. Empirical Execution Log (`RazorpayClientWrapper`)

### Live Creation Call:

```python
from app.graph.executor import executor_node

# Input State:
state = {
    "case_id": "case_test_rzp",
    "recovery_channel": "payment_link",
    "recovery_action": "send_payment_link",
    "message_content": "Complete your payment for Vaapsi recovery",
    "amount_at_risk": 1499.0,
    "customer_email": "customer@example.com",
    "customer_phone": "+919876543210"
}

# Execution:
res = executor_node(state)
```

### Returned Live Razorpay API Payload:

```json
{
  "execution_status": "success",
  "execution_result": {
    "delivered": true,
    "delivery_id": "dlv_7fbfc2b97551",
    "channel": "payment_link",
    "payment_link_id": "plink_TVkw3QqPFxCt3b",
    "payment_link_url": "https://rzp.io/rzp/V1WNpGao",
    "amount": 1499.0,
    "note": "[RAZORPAY TEST API] Created payment link plink_TVkw3QqPFxCt3b",
    "simulated": false
  }
}
```

---

## 🔗 3. Verified Razorpay Live Payment Link URLs

| Link ID | Live Razorpay Gateway URL | Status | Gateway Interface |
|---|---|---|---|
| **`plink_TVkw3QqPFxCt3b`** | [`https://rzp.io/rzp/V1WNpGao`](https://rzp.io/rzp/V1WNpGao) | `created` (`simulated: false`) | Opens live Razorpay test-mode checkout page |
| **`plink_TVkvGpvLUzwuDa`** | [`https://rzp.io/rzp/625AhIu3`](https://rzp.io/rzp/625AhIu3) | `created` (`simulated: false`) | Opens live Razorpay test-mode checkout page |

* **Interactive Proof:** Opening either URL above in a web browser displays the official Razorpay payment gateway interface where test payments can be completed.
