"""
Recoup — Evaluation Harness.

Runs evaluation against held-out dataset and generates comparative report.

Usage:
    python evals/harness.py --smoke-test
    python evals/harness.py --full
"""

import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Add project root and agent service to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "apps" / "agent-service"))

from app.graph.pipeline import process_event
from app.classifiers.root_causes import RETRYABLE_ROOT_CAUSES
from data.generator.decline_codes import DECLINE_CODE_MAP
from evals.metrics.calculator import (
    calculate_latency_percentiles,
    calculate_classification_metrics,
    compare_baselines,
)
from evals.reports.report_generator import generate_markdown_report

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def run_naive_retry_baseline(events: list[dict]) -> float:
    """
    Naive Retry Baseline:
    Retries every payment_failed event blindly once.
    Recovers payments if the decline code is retryable.
    """
    total_recovered = 0.0

    for e in events:
        if e.get("event_type") == "payment_failed":
            decline_code = e.get("decline_code", "").upper()
            mapping = DECLINE_CODE_MAP.get(decline_code)
            # Naive retry succeeds for simple transient codes like NSF or BANK_DOWN
            if mapping and mapping.is_retryable:
                total_recovered += e.get("amount", 0.0) * 0.40  # 40% naive retry success rate

    return total_recovered


def run_eval_harness(smoke_test: bool = False) -> dict:
    """Run full evaluation suite on held-out dataset."""

    samples_dir = ROOT_DIR / "data" / "samples"
    file_name = "tuning_set.json" if smoke_test else "held_out_set.json"
    data_path = samples_dir / file_name

    if not data_path.exists():
        # Fall back to tuning set if held-out set doesn't exist
        data_path = samples_dir / "tuning_set.json"

    with open(data_path, "r", encoding="utf-8") as f:
        events = json.load(f)

    if smoke_test:
        events = events[:15]

    total_at_risk = sum(e.get("amount", e.get("cart_value", 0.0)) for e in events)

    # 1. Run Naive Retry Baseline
    naive_recovered = run_naive_retry_baseline(events)

    # 2. Run Recoup Agent Pipeline
    recoup_recovered = 0.0
    latencies = []
    predictions = []
    rule_hits = 0
    llm_hits = 0
    compliance_violations = 0

    print(f"[*] Running Recoup Agent Pipeline over {len(events)} test events...")

    for idx, event in enumerate(events):
        t0 = time.monotonic()
        res = process_event(event)
        elapsed_ms = (time.monotonic() - t0) * 1000
        latencies.append(elapsed_ms)

        # Revenue
        recoup_recovered += res.get("recovery_amount", 0.0)

        # Method
        method = res.get("diagnosis_method", "")
        if method == "rule":
            rule_hits += 1
        else:
            llm_hits += 1

        # Classification ground truth (expected root cause)
        decline_code = event.get("decline_code", "").upper()
        mapping = DECLINE_CODE_MAP.get(decline_code)
        expected = mapping.root_cause.value if mapping else "unknown"
        predicted = res.get("root_cause", "unknown")
        predictions.append({"expected": expected, "predicted": predicted})

        # Compliance
        if res.get("guardrail_status") == "approved":
            for v in res.get("guardrail_violations", []):
                if v.startswith("OPTED_OUT") or v.startswith("MAX_RETRIES"):
                    compliance_violations += 1

    # 3. Calculate Metrics
    latency_stats = calculate_latency_percentiles(latencies)
    classification_stats = calculate_classification_metrics(predictions)
    baseline_stats = compare_baselines(total_at_risk, recoup_recovered, naive_recovered)
    rule_ratio = (rule_hits / len(events) * 100) if events else 0.0

    eval_summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_events": len(events),
        "rule_hits": rule_hits,
        "llm_hits": llm_hits,
        "rule_hit_ratio": rule_ratio,
        "compliance_violations": compliance_violations,
        "latencies": latency_stats,
        "classification": classification_stats,
        "baseline_comparison": baseline_stats,
    }

    return eval_summary


def main():
    parser = argparse.ArgumentParser(description="Recoup Agent Evaluation Harness")
    parser.add_argument("--smoke-test", action="store_true", help="Run quick smoke test on 15 events")
    parser.add_argument("--full", action="store_true", help="Run full evaluation on held-out dataset")
    args = parser.parse_args()

    smoke = args.smoke_test or (not args.full)
    mode = "Smoke Test" if smoke else "Full Evaluation"

    print(f"\n==========================================")
    print(f"  Recoup Agent Evaluation Harness ({mode})")
    print(f"==========================================\n")

    summary = run_eval_harness(smoke_test=smoke)

    # Generate Markdown Report
    report_md = generate_markdown_report(summary)

    reports_dir = ROOT_DIR / "evals" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "report.md"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"[OK] Evaluation complete!")
    print(f"[REPORT] Report generated -> {report_path}\n")
    print(report_md)


if __name__ == "__main__":
    main()
