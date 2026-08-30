"""
Recoup — Synthetic Data Generator.

Produces 300+ realistic events across:
- Failed payments (50%) with varied decline reasons
- Abandoned checkouts (30%) with cart/device/timing data
- Failed subscription mandates (20%) with attempt/overdue info

Includes intentional noise: ~5% duplicates, ~3% out-of-order timestamps,
~10% ambiguous decline reasons.

Usage:
    python -m data.generator.generate
    python -m data.generator.generate --seed 42 --total 500
"""

import json
import random
import sys
import uuid
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from data.generator.decline_codes import (
    DECLINE_CODE_MAP,
    AMBIGUOUS_DECLINE_REASONS,
    RootCause,
)


# ============================================
# Constants
# ============================================

INDIAN_BANKS = [
    "HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Kotak Mahindra",
    "Punjab National Bank", "Bank of Baroda", "Yes Bank", "IndusInd Bank",
    "Federal Bank", "IDBI Bank", "Canara Bank", "Union Bank",
]

INDIAN_FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh",
    "Ayaan", "Krishna", "Ishaan", "Ananya", "Diya", "Saanvi", "Aanya",
    "Aadhya", "Isha", "Myra", "Priya", "Riya", "Kavya", "Rohan",
    "Raj", "Amit", "Deepak", "Suresh", "Neha", "Pooja", "Swati",
]

INDIAN_LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Gupta", "Agarwal", "Reddy",
    "Verma", "Joshi", "Shah", "Mehta", "Nair", "Iyer", "Pillai",
    "Das", "Bose", "Chatterjee", "Mukherjee", "Banerjee", "Roy",
]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com"]

PRODUCT_CATEGORIES = [
    "Electronics", "Fashion", "Home & Kitchen", "Books", "Health & Beauty",
    "Sports", "Toys & Games", "Automotive", "Grocery", "Jewelry",
]

SUBSCRIPTION_PLANS = [
    {"id": "plan_basic", "name": "Basic Plan", "amount": 199},
    {"id": "plan_pro", "name": "Pro Plan", "amount": 499},
    {"id": "plan_premium", "name": "Premium Plan", "amount": 999},
    {"id": "plan_enterprise", "name": "Enterprise Plan", "amount": 2999},
    {"id": "plan_monthly", "name": "Monthly Box", "amount": 799},
    {"id": "plan_annual", "name": "Annual Membership", "amount": 4999},
]


def generate_customer_id() -> str:
    """Generate a realistic Razorpay-style customer ID."""
    return f"cust_{uuid.uuid4().hex[:14]}"


def generate_payment_id() -> str:
    return f"pay_{uuid.uuid4().hex[:14]}"


def generate_order_id() -> str:
    return f"order_{uuid.uuid4().hex[:14]}"


def generate_subscription_id() -> str:
    return f"sub_{uuid.uuid4().hex[:14]}"


def generate_event_id() -> str:
    return f"evt_{uuid.uuid4().hex[:16]}"


def generate_customer(rng: random.Random) -> dict:
    """Generate a realistic Indian customer."""
    first = rng.choice(INDIAN_FIRST_NAMES)
    last = rng.choice(INDIAN_LAST_NAMES)
    domain = rng.choice(EMAIL_DOMAINS)
    phone_prefix = rng.choice(["91", "91", "91"])  # Indian numbers
    phone = f"+{phone_prefix}{rng.randint(7000000000, 9999999999)}"

    return {
        "id": generate_customer_id(),
        "name": f"{first} {last}",
        "email": f"{first.lower()}.{last.lower()}{rng.randint(1, 999)}@{domain}",
        "phone": phone,
    }


def generate_timestamp(rng: random.Random, base_time: datetime) -> str:
    """Generate a timestamp within 7 days of base_time."""
    offset = timedelta(
        days=rng.randint(0, 6),
        hours=rng.randint(0, 23),
        minutes=rng.randint(0, 59),
        seconds=rng.randint(0, 59),
    )
    return (base_time + offset).isoformat()


AMBIGUOUS_GROUND_TRUTH = {
    "DO_NOT_HONOR": "risk_declined",
    "GENERAL_DECLINE": "issuer_unavailable",
    "DECLINE": "issuer_unavailable",
    "PROCESSING_ERROR": "network_error",
    "SYSTEM_ERROR": "issuer_unavailable",
    "UNKNOWN_ERROR": "issuer_unavailable",
    "CONTACT_BANK": "customer_action_needed",
    "REFER_TO_ISSUER": "customer_action_needed",
    "TRY_AGAIN": "network_error",
    "NOT_PERMITTED": "risk_declined",
    "SERVICE_NOT_ALLOWED": "limit_exceeded",
}

MANDATE_GROUND_TRUTH = {
    "INSUFFICIENT_FUNDS": "insufficient_funds",
    "BANK_DOWN": "issuer_unavailable",
    "MANDATE_NOT_APPROVED": "mandate_issue",
    "DEBIT_FAILED": "mandate_issue",
    "MANDATE_REVOKED": "mandate_issue",
    "NETWORK_ERROR": "network_error",
    "DO_NOT_HONOR": "risk_declined",
    "GENERAL_DECLINE": "issuer_unavailable",
}


def generate_payment_failed_event(rng: random.Random, base_time: datetime) -> dict:
    """Generate a failed payment event."""
    # Decide if this is a known decline code or an ambiguous one
    if rng.random() < 0.10:  # 10% ambiguous — goes to LLM fallback
        decline_code = rng.choice(AMBIGUOUS_DECLINE_REASONS)
        decline_reason = f"Transaction declined: {decline_code}"
        ground_truth = AMBIGUOUS_GROUND_TRUTH.get(decline_code, "issuer_unavailable")
    else:  # 90% known codes — rules engine handles
        decline_code = rng.choice(list(DECLINE_CODE_MAP.keys()))
        mapping = DECLINE_CODE_MAP[decline_code]
        decline_reason = mapping.description
        ground_truth = mapping.root_cause.value

    # Realistic payment amounts
    amount_tiers = [
        (0.3, (100, 999)),      # Small: ₹100–999
        (0.4, (1000, 4999)),    # Medium: ₹1000–4999
        (0.2, (5000, 14999)),   # Large: ₹5000–14999
        (0.1, (15000, 50000)),  # Very large: ₹15000–50000
    ]
    tier = rng.random()
    cumulative = 0
    amount_range = (1000, 4999)
    for prob, range_ in amount_tiers:
        cumulative += prob
        if tier <= cumulative:
            amount_range = range_
            break

    amount = round(rng.uniform(*amount_range), 2)
    method = rng.choice(["card", "card", "card", "upi", "netbanking", "wallet"])

    return {
        "event_id": generate_event_id(),
        "event_type": "payment_failed",
        "payment_id": generate_payment_id(),
        "order_id": generate_order_id(),
        "amount": amount,
        "currency": "INR",
        "decline_reason": decline_reason,
        "decline_code": decline_code,
        "ground_truth_root_cause": ground_truth,
        "method": method,
        "bank": rng.choice(INDIAN_BANKS),
        "customer": generate_customer(rng),
        "timestamp": generate_timestamp(rng, base_time),
        "metadata": {
            "category": rng.choice(PRODUCT_CATEGORIES),
            "retry_eligible": decline_code not in ["MANDATE_REVOKED", "FRAUD_SUSPECTED"],
        },
    }


def generate_checkout_abandoned_event(rng: random.Random, base_time: datetime) -> dict:
    """Generate an abandoned checkout event."""
    cart_tiers = [
        (0.25, (200, 999)),
        (0.35, (1000, 4999)),
        (0.25, (5000, 14999)),
        (0.15, (15000, 75000)),
    ]
    tier = rng.random()
    cumulative = 0
    cart_range = (1000, 4999)
    for prob, range_ in cart_tiers:
        cumulative += prob
        if tier <= cumulative:
            cart_range = range_
            break

    cart_value = round(rng.uniform(*cart_range), 2)

    # Time to abandon — most abandon quickly
    abandon_tiers = [
        (0.3, (10, 60)),      # Quick abandoners
        (0.4, (60, 300)),     # 1–5 minutes
        (0.2, (300, 900)),    # 5–15 minutes
        (0.1, (900, 3600)),   # Long browsers
    ]
    tier = rng.random()
    cumulative = 0
    time_range = (60, 300)
    for prob, range_ in abandon_tiers:
        cumulative += prob
        if tier <= cumulative:
            time_range = range_
            break

    # Generate main fields using primary RNG stream first
    time_to_abandon = rng.randint(*time_range)
    device_type = rng.choice(["mobile", "mobile", "mobile", "desktop", "tablet"])
    channel = rng.choice(["web", "web", "app", "social"])
    items_count = rng.randint(1, 8)
    customer = generate_customer(rng)
    timestamp = generate_timestamp(rng, base_time)
    category = rng.choice(PRODUCT_CATEGORIES)
    page_views = rng.randint(1, 20)
    event_id = generate_event_id()
    order_id = generate_order_id()

    # Synthetic ground-truth reason assigned via isolated RNG stream
    # to preserve 100% main RNG stream invariance
    gt_rng = random.Random(f"gt_{event_id}")
    abandon_reasons = ["checkout_friction", "price_sensitivity", "comparison_shopping"]
    ground_truth = gt_rng.choices(abandon_reasons, weights=[50, 30, 20])[0]

    return {
        "event_id": event_id,
        "event_type": "checkout_abandoned",
        "order_id": order_id,
        "cart_value": cart_value,
        "currency": "INR",
        "ground_truth_root_cause": ground_truth,
        "time_to_abandon_seconds": time_to_abandon,
        "device_type": device_type,
        "channel": channel,
        "items_count": items_count,
        "customer": customer,
        "timestamp": timestamp,
        "metadata": {
            "category": category,
            "page_views": page_views,
        },
    }


def generate_mandate_failed_event(rng: random.Random, base_time: datetime) -> dict:
    """Generate a failed subscription mandate event."""
    plan = rng.choice(SUBSCRIPTION_PLANS)
    attempt_number = rng.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
    days_overdue = rng.randint(0, attempt_number * 7)

    failure_reasons = [
        "INSUFFICIENT_FUNDS", "BANK_DOWN", "MANDATE_NOT_APPROVED",
        "DEBIT_FAILED", "MANDATE_REVOKED", "NETWORK_ERROR",
        "DO_NOT_HONOR", "GENERAL_DECLINE",
    ]

    failure_reason = rng.choice(failure_reasons)
    ground_truth = MANDATE_GROUND_TRUTH.get(failure_reason, "mandate_issue")

    return {
        "event_id": generate_event_id(),
        "event_type": "mandate_failed",
        "subscription_id": generate_subscription_id(),
        "plan_id": plan["id"],
        "amount": plan["amount"],
        "currency": "INR",
        "attempt_number": attempt_number,
        "days_overdue": days_overdue,
        "mandate_type": rng.choice(["emandate", "nach", "upi_autopay"]),
        "failure_reason": failure_reason,
        "ground_truth_root_cause": ground_truth,
        "customer": generate_customer(rng),
        "timestamp": generate_timestamp(rng, base_time),
        "metadata": {
            "plan_name": plan["name"],
            "billing_cycle": "monthly",
        },
    }


def inject_noise(events: list[dict], rng: random.Random) -> list[dict]:
    """
    Inject realistic noise into the event stream:
    - ~5% duplicate events
    - ~3% out-of-order timestamps
    """
    noisy_events = list(events)

    # Add duplicates (~5%)
    num_duplicates = max(1, int(len(events) * 0.05))
    for _ in range(num_duplicates):
        original = rng.choice(events)
        duplicate = dict(original)
        # Same event_id = duplicate webhook delivery
        noisy_events.append(duplicate)

    # Shuffle to create out-of-order timestamps (~3%)
    num_swaps = max(1, int(len(noisy_events) * 0.03))
    for _ in range(num_swaps):
        i = rng.randint(0, len(noisy_events) - 2)
        noisy_events[i], noisy_events[i + 1] = noisy_events[i + 1], noisy_events[i]

    return noisy_events


def generate_batch(
    total: int = 300,
    seed: int = 42,
    tuning_ratio: float = 0.67,  # 67% tuning, 33% held-out
) -> tuple[list[dict], list[dict], dict]:
    """
    Generate a full batch of synthetic events.

    Returns:
        (tuning_set, held_out_set, metadata)
    """
    rng = random.Random(seed)
    base_time = datetime(2026, 8, 20, 0, 0, 0, tzinfo=timezone.utc)

    # Distribution: 50% payment_failed, 30% checkout_abandoned, 20% mandate_failed
    num_payment_failed = int(total * 0.50)
    num_checkout_abandoned = int(total * 0.30)
    num_mandate_failed = total - num_payment_failed - num_checkout_abandoned

    events = []

    for _ in range(num_payment_failed):
        events.append(generate_payment_failed_event(rng, base_time))

    for _ in range(num_checkout_abandoned):
        events.append(generate_checkout_abandoned_event(rng, base_time))

    for _ in range(num_mandate_failed):
        events.append(generate_mandate_failed_event(rng, base_time))

    # Sort by timestamp
    events.sort(key=lambda e: e["timestamp"])

    # Inject noise
    events = inject_noise(events, rng)

    # Split into tuning and held-out
    split_idx = int(len(events) * tuning_ratio)
    tuning_set = events[:split_idx]
    held_out_set = events[split_idx:]

    # Calculate distribution stats
    def count_types(evts):
        counts = {"payment_failed": 0, "checkout_abandoned": 0, "mandate_failed": 0}
        for e in evts:
            counts[e["event_type"]] += 1
        return counts

    # Count duplicates
    event_ids = [e["event_id"] for e in events]
    unique_ids = set(event_ids)
    num_duplicates = len(event_ids) - len(unique_ids)

    metadata = {
        "batch_id": f"batch_{uuid.uuid4().hex[:8]}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "total_events_raw": total,
        "total_events_with_noise": len(events),
        "tuning_set_size": len(tuning_set),
        "held_out_set_size": len(held_out_set),
        "duplicates_injected": num_duplicates,
        "distribution": {
            "all": count_types(events),
            "tuning": count_types(tuning_set),
            "held_out": count_types(held_out_set),
        },
        "amount_stats": {
            "total_at_risk": round(sum(
                e.get("amount", e.get("cart_value", 0)) for e in events
            ), 2),
            "avg_amount": round(
                sum(e.get("amount", e.get("cart_value", 0)) for e in events) / len(events),
                2,
            ),
        },
    }

    return tuning_set, held_out_set, metadata


def main():
    """Generate and save synthetic data."""
    parser = argparse.ArgumentParser(description="Generate synthetic events for Recoup")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--total", type=int, default=300, help="Total events to generate")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "samples"),
        help="Output directory",
    )
    args = parser.parse_args()

    print(f"[*] Generating {args.total} synthetic events with seed={args.seed}...")

    tuning_set, held_out_set, metadata = generate_batch(
        total=args.total,
        seed=args.seed,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save tuning set
    tuning_path = output_dir / "tuning_set.json"
    with open(tuning_path, "w", encoding="utf-8") as f:
        json.dump(tuning_set, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Tuning set: {len(tuning_set)} events -> {tuning_path}")

    # Save held-out set
    held_out_path = output_dir / "held_out_set.json"
    with open(held_out_path, "w", encoding="utf-8") as f:
        json.dump(held_out_set, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Held-out set: {len(held_out_set)} events -> {held_out_path}")

    # Save metadata
    meta_path = output_dir / "metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Metadata -> {meta_path}")

    # Summary
    print(f"\n[SUMMARY]")
    print(f"  Total events (with noise): {metadata['total_events_with_noise']}")
    print(f"  Duplicates injected: {metadata['duplicates_injected']}")
    print(f"  Total INR at risk: {metadata['amount_stats']['total_at_risk']:,.2f}")
    print(f"  Distribution: {metadata['distribution']['all']}")


if __name__ == "__main__":
    main()
