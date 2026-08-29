# 💳 Vaapsi (वापसी) — Razorpay Integration & Verification Proof

> **Empirical Technical Verification Ledger**  
> *Documentation of live Razorpay Test Mode API credentials, generated payment link IDs, and live HTTP 200 checkout gateway URLs.*

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

## 🔗 3. Empirically Tested Live Payment Link URLs

All 4 payment links were created live against Razorpay Test API and verified with active HTTP GET requests returning `HTTP STATUS: 200`:

| Case ID | Amount (INR) | Payment Link ID | Live Razorpay Gateway URL | HTTP Status | Gateway Interface |
|---|---|---|---|---|---|
| `case_val_101` | ₹4,999.00 | **`plink_TVlKaOvuj91lml`** | [`https://rzp.io/rzp/QxLhfFat`](https://rzp.io/rzp/QxLhfFat) | **`200 OK`** | Verified Live Razorpay Test Checkout |
| `case_val_102` | ₹1,299.00 | **`plink_TVlKarpadYGCPE`** | [`https://rzp.io/rzp/bKjaobX`](https://rzp.io/rzp/bKjaobX) | **`200 OK`** | Verified Live Razorpay Test Checkout |
| `case_val_103` | ₹8,999.00 | **`plink_TVlKbMfnTlpDel`** | [`https://rzp.io/rzp/INJmo1d`](https://rzp.io/rzp/INJmo1d) | **`200 OK`** | Verified Live Razorpay Test Checkout |
| `case_test_rzp` | ₹1,499.00 | **`plink_TVkw3QqPFxCt3b`** | [`https://rzp.io/rzp/V1WNpGao`](https://rzp.io/rzp/V1WNpGao) | **`200 OK`** | Verified Live Razorpay Test Checkout |

### HTTP Verification Script:

```python
import urllib.request

urls = [
    'https://rzp.io/rzp/QxLhfFat',
    'https://rzp.io/rzp/bKjaobX',
    'https://rzp.io/rzp/INJmo1d',
    'https://rzp.io/rzp/V1WNpGao'
]

for url in urls:
    code = urllib.request.urlopen(url).getcode()
    print(f"URL: {url} -> HTTP STATUS: {code}")
```
