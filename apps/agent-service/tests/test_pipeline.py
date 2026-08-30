"""
Recoup — Pipeline smoke test.

Runs a few synthetic events through the full LangGraph pipeline
and validates the output state.
"""

import json
import sys
from pathlib import Path

# Add the agent service to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# Add project root for data imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.graph.pipeline import process_event, process_batch


def test_single_payment_failed():
    """Test a single failed payment event."""
    event = {
        "event_id": "evt_test_001",
        "event_type": "payment_failed",
        "payment_id": "pay_test_001",
        "order_id": "order_test_001",
        "amount": 2499.00,
        "currency": "INR",
        "decline_reason": "Card has insufficient funds to complete the transaction",
        "decline_code": "INSUFFICIENT_FUNDS",
        "method": "card",
        "bank": "HDFC Bank",
        "customer": {
            "id": "cust_test_001",
            "email": "aarav.sharma@gmail.com",
            "phone": "+919876543210",
            "name": "Aarav Sharma",
        },
        "timestamp": "2026-08-20T10:30:00+00:00",
    }

    result = process_event(event)

    # Assertions
    assert result["case_status"] in ("recovered", "failed"), f"Unexpected status: {result['case_status']}"
    assert result["root_cause"] == "insufficient_funds", f"Wrong root cause: {result['root_cause']}"
    assert result["diagnosis_method"] == "rule", f"Should use rules engine: {result['diagnosis_method']}"
    assert result["root_cause_confidence"] >= 0.9, "Rules engine should give high confidence"
    assert result["recovery_channel"] == "payment_link", f"Wrong channel: {result['recovery_channel']}"
    assert len(result["audit_trail"]) >= 5, f"Should have 5+ audit entries, got {len(result['audit_trail'])}"
    assert result["guardrail_status"] == "approved", f"Should be approved: {result['guardrail_status']}"

    print(f"  [OK] Payment failed: root_cause={result['root_cause']}, "
          f"method={result['diagnosis_method']}, status={result['case_status']}, "
          f"recovery=INR {result.get('recovery_amount', 0):,.2f}")


def test_checkout_abandoned():
    """Test a checkout abandoned event."""
    event = {
        "event_id": "evt_test_002",
        "event_type": "checkout_abandoned",
        "order_id": "order_test_002",
        "cart_value": 3999.00,
        "currency": "INR",
        "time_to_abandon_seconds": 180,
        "device_type": "mobile",
        "channel": "app",
        "items_count": 3,
        "customer": {
            "id": "cust_test_002",
            "email": "priya.patel@gmail.com",
            "phone": "+919876543211",
            "name": "Priya Patel",
        },
        "timestamp": "2026-08-20T14:15:00+00:00",
    }

    result = process_event(event)

    assert result["root_cause"] == "checkout_friction", f"Wrong root cause: {result['root_cause']}"
    assert result["recovery_channel"] == "email", f"Wrong channel: {result['recovery_channel']}"

    print(f"  [OK] Checkout abandoned: root_cause={result['root_cause']}, "
          f"channel={result['recovery_channel']}, status={result['case_status']}")


def test_ambiguous_decline():
    """Test an ambiguous decline code that should hit LLM fallback."""
    event = {
        "event_id": "evt_test_003",
        "event_type": "payment_failed",
        "payment_id": "pay_test_003",
        "amount": 1500.00,
        "currency": "INR",
        "decline_reason": "Transaction declined",
        "decline_code": "DO_NOT_HONOR",
        "method": "card",
        "bank": "SBI",
        "customer": {
            "id": "cust_test_003",
            "email": "rohan.kumar@gmail.com",
            "phone": "+919876543212",
            "name": "Rohan Kumar",
        },
        "timestamp": "2026-08-20T16:00:00+00:00",
    }

    result = process_event(event)

    # Should attempt LLM fallback for ambiguous codes
    assert result["diagnosis_method"] == "llm_fallback", f"Should use LLM: {result['diagnosis_method']}"

    print(f"  [OK] Ambiguous decline: root_cause={result['root_cause']}, "
          f"method={result['diagnosis_method']}, provider={result['diagnosis_provider']}, "
          f"confidence={result['root_cause_confidence']:.2f}")


def test_opted_out_customer():
    """Test that opted-out customer is blocked by guardrail."""
    event = {
        "event_id": "evt_test_004",
        "event_type": "payment_failed",
        "payment_id": "pay_test_004",
        "amount": 999.00,
        "currency": "INR",
        "decline_reason": "Insufficient funds",
        "decline_code": "INSUFFICIENT_FUNDS",
        "method": "card",
        "bank": "ICICI Bank",
        "customer": {
            "id": "cust_test_004",
            "email": "opted.out@gmail.com",
            "phone": "+919876543213",
            "name": "Opted Out User",
        },
        "timestamp": "2026-08-20T11:00:00+00:00",
    }

    # Manually set opted-out in the pipeline
    from app.graph.pipeline import recovery_pipeline
    import uuid
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    initial_state = {
        "case_id": f"case_{uuid.uuid4().hex[:12]}",
        "event_id": event["event_id"],
        "event_type": event["event_type"],
        "raw_event": event,
        "customer_id": "",
        "customer_email": "",
        "customer_phone": "",
        "customer_name": "",
        "customer_opted_out": True,  # <-- opted out
        "amount_at_risk": 0.0,
        "currency": "INR",
        "decline_reason_raw": "",
        "root_cause": "",
        "root_cause_confidence": 0.0,
        "diagnosis_method": "",
        "diagnosis_reasoning": "",
        "diagnosis_provider": "",
        "diagnosis_latency_ms": 0.0,
        "recovery_channel": "",
        "recovery_action": "",
        "message_content": "",
        "offer_details": {},
        "scheduled_at": "",
        "guardrail_status": "",
        "guardrail_violations": [],
        "execution_status": "",
        "execution_result": {},
        "razorpay_payment_link_id": "",
        "recovery_amount": 0.0,
        "case_status": "detected",
        "retry_count": 0,
        "idempotency_key": event["event_id"],
        "audit_trail": [],
        "created_at": now,
        "updated_at": now,
    }

    result = recovery_pipeline.invoke(initial_state)

    assert result["guardrail_status"] == "blocked", f"Should be blocked: {result['guardrail_status']}"
    assert result["case_status"] == "blocked", f"Should be blocked status: {result['case_status']}"
    assert any("OPTED_OUT" in v for v in result["guardrail_violations"]), "Should have OPTED_OUT violation"

    print(f"  [OK] Opted-out customer: guardrail={result['guardrail_status']}, "
          f"violations={result['guardrail_violations']}")


def test_batch_from_synthetic_data():
    """Test a small batch from generated synthetic data."""
    samples_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "samples" / "tuning_set.json"

    if not samples_path.exists():
        print("  [SKIP] Synthetic data not found, run generate.py first")
        return

    with open(samples_path, "r", encoding="utf-8") as f:
        all_events = json.load(f)

    # Process first 10 events
    batch = all_events[:10]
    results = process_batch(batch)

    # Aggregate stats
    statuses = {}
    methods = {"rule": 0, "llm_fallback": 0}
    total_recovered = 0
    total_at_risk = 0

    for r in results:
        status = r.get("case_status", "unknown")
        statuses[status] = statuses.get(status, 0) + 1
        method = r.get("diagnosis_method", "")
        if method in methods:
            methods[method] += 1
        total_recovered += r.get("recovery_amount", 0)
        total_at_risk += r.get("amount_at_risk", 0)

    recovery_rate = (total_recovered / total_at_risk * 100) if total_at_risk > 0 else 0
    rule_ratio = methods["rule"] / len(results) * 100 if results else 0

    print(f"  [OK] Batch of {len(results)} events processed")
    print(f"       Statuses: {statuses}")
    print(f"       Rule hits: {methods['rule']}/{len(results)} ({rule_ratio:.0f}%)")
    print(f"       Recovery: INR {total_recovered:,.2f} / {total_at_risk:,.2f} ({recovery_rate:.1f}%)")


if __name__ == "__main__":
    print("\n=== Recoup Pipeline Smoke Test ===\n")

    print("[1] Payment Failed (known decline code):")
    test_single_payment_failed()

    print("\n[2] Checkout Abandoned:")
    test_checkout_abandoned()

    print("\n[3] Ambiguous Decline (LLM fallback):")
    test_ambiguous_decline()

    print("\n[4] Opted-Out Customer (guardrail block):")
    test_opted_out_customer()

    print("\n[5] Batch from Synthetic Data:")
    test_batch_from_synthetic_data()

    print("\n=== All smoke tests passed! ===\n")
