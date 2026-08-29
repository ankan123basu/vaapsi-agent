"""
Recoup — Evaluation Metrics Calculator.

Computes precision, recall, F1 score, recovery lift over baselines,
latency percentiles (p50/p95), and compliance metrics.
"""

import math
from typing import List, Dict, Any, Tuple


def calculate_latency_percentiles(latencies: List[float]) -> Dict[str, float]:
    """Calculate p50 and p95 latencies from a list of millisecond values."""
    if not latencies:
        return {"p50": 0.0, "p95": 0.0, "mean": 0.0}

    sorted_lats = sorted(latencies)
    n = len(sorted_lats)

    p50_idx = int(math.ceil(0.50 * n)) - 1
    p95_idx = int(math.ceil(0.95 * n)) - 1

    p50 = sorted_lats[max(0, p50_idx)]
    p95 = sorted_lats[max(0, p95_idx)]
    mean = sum(sorted_lats) / n

    return {
        "p50": round(p50, 2),
        "p95": round(p95, 2),
        "mean": round(mean, 2),
    }


def calculate_classification_metrics(predictions: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Compute precision, recall, F1, and confusion matrix for root cause classification.

    predictions element format:
    {"expected": "insufficient_funds", "predicted": "insufficient_funds"}
    """
    categories = set()
    for p in predictions:
        categories.add(p["expected"])
        categories.add(p["predicted"])

    categories = sorted(list(categories))

    # Confusion matrix
    matrix: Dict[str, Dict[str, int]] = {c1: {c2: 0 for c2 in categories} for c1 in categories}

    for p in predictions:
        matrix[p["expected"]][p["predicted"]] += 1

    # Per-category metrics
    per_category = {}
    total_tp = 0
    total_samples = len(predictions)

    for cat in categories:
        tp = matrix[cat][cat]
        fp = sum(matrix[other][cat] for other in categories if other != cat)
        fn = sum(matrix[cat][other] for other in categories if other != cat)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        total_tp += tp

        per_category[cat] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": tp + fn,
        }

    overall_accuracy = total_tp / total_samples if total_samples > 0 else 0.0

    return {
        "overall_accuracy": round(overall_accuracy, 4),
        "per_category": per_category,
        "confusion_matrix": matrix,
        "categories": categories,
    }


def compare_baselines(
    at_risk: float,
    recoup_recovered: float,
    naive_retry_recovered: float,
) -> Dict[str, Any]:
    """Compare Recoup performance against Do-Nothing and Naive-Retry baselines."""
    do_nothing_rec = 0.0

    do_nothing_rate = 0.0
    naive_retry_rate = (naive_retry_recovered / at_risk * 100) if at_risk > 0 else 0.0
    recoup_rate = (recoup_recovered / at_risk * 100) if at_risk > 0 else 0.0

    lift_over_do_nothing = recoup_recovered
    lift_over_naive = recoup_recovered - naive_retry_recovered
    percentage_lift_over_naive = (
        ((recoup_recovered - naive_retry_recovered) / naive_retry_recovered * 100)
        if naive_retry_recovered > 0
        else 100.0
    )

    return {
        "total_at_risk": round(at_risk, 2),
        "do_nothing": {"recovered": 0.0, "rate_pct": 0.0},
        "naive_retry": {"recovered": round(naive_retry_recovered, 2), "rate_pct": round(naive_retry_rate, 2)},
        "recoup": {"recovered": round(recoup_recovered, 2), "rate_pct": round(recoup_rate, 2)},
        "abs_lift_over_naive": round(lift_over_naive, 2),
        "pct_lift_over_naive": round(percentage_lift_over_naive, 2),
    }
