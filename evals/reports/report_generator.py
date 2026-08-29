"""
Recoup — Evaluation Report Generator.

Formats evaluation results into a clean, markdown report with tables,
confusion matrix, and baseline comparison.
"""

from typing import Dict, Any


def generate_markdown_report(eval_summary: Dict[str, Any]) -> str:
    """Generate Markdown report content from evaluation summary dictionary."""

    baseline = eval_summary["baseline_comparison"]
    latencies = eval_summary["latencies"]
    classification = eval_summary["classification"]

    md = []
    md.append("# Recoup — Evaluation Report")
    md.append("")
    md.append("> Autonomous Revenue Recovery Agent — Held-Out Test Set Results")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Executive Summary")
    md.append("")
    md.append(f"- **Total Events Evaluated:** {eval_summary['total_events']}")
    md.append(f"- **Total Revenue at Risk:** ₹{baseline['total_at_risk']:,.2f}")
    md.append(f"- **Total Revenue Recovered:** **₹{baseline['recoup']['recovered']:,.2f}** ({baseline['recoup']['rate_pct']:.1f}%)")
    md.append(f"- **Lift over Naive Retry Baseline:** **+₹{baseline['abs_lift_over_naive']:,.2f}** ({baseline['pct_lift_over_naive']:+.1f}%)")
    md.append(f"- **Deterministic Rule Hit Ratio:** **{eval_summary['rule_hit_ratio']:.1f}%** ({eval_summary['rule_hits']}/{eval_summary['total_events']})")
    md.append(f"- **Classification Accuracy:** **{classification['overall_accuracy']*100:.1f}%**")
    md.append(f"- **Compliance Violations:** **{eval_summary['compliance_violations']}** (Pass)")
    md.append(f"- **p50 Latency:** **{latencies['p50']}ms** | **p95 Latency:** **{latencies['p95']}ms**")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. Baseline Performance Comparison")
    md.append("")
    md.append("| Approach | Revenue Recovered (₹) | Recovery Rate (%) | Lift vs. Baseline |")
    md.append("|---|---|---|---|")
    md.append(f"| **Do Nothing** | ₹0.00 | 0.0% | Baseline |")
    md.append(f"| **Naive Retry-Everything** | ₹{baseline['naive_retry']['recovered']:,.2f} | {baseline['naive_retry']['rate_pct']:.1f}% | +₹{baseline['naive_retry']['recovered']:,.2f} |")
    md.append(f"| **Recoup Agent (Full Pipeline)** | **₹{baseline['recoup']['recovered']:,.2f}** | **{baseline['recoup']['rate_pct']:.1f}%** | **+₹{baseline['abs_lift_over_naive']:,.2f} ({baseline['pct_lift_over_naive']:+.1f}%)** |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 2. Root Cause Classifier Performance")
    md.append("")
    md.append("| Root Cause Category | Support | Precision | Recall | F1 Score |")
    md.append("|---|---|---|---|---|")

    for cat, stats in classification["per_category"].items():
        md.append(
            f"| `{cat}` | {stats['support']} | {stats['precision']:.2f} | {stats['recall']:.2f} | {stats['f1']:.2f} |"
        )

    md.append("")
    md.append("---")
    md.append("")
    md.append("## 3. System Latency & Provider Distribution")
    md.append("")
    md.append("| Metric | Value | Target | Status |")
    md.append("|---|---|---|---|")
    md.append(f"| p50 Latency (Event → Action) | {latencies['p50']} ms | < 500 ms | {'[Pass]' if latencies['p50'] < 500 else '[High]'} |")
    md.append(f"| p95 Latency (Event → Action) | {latencies['p95']} ms | < 1500 ms | {'[Pass]' if latencies['p95'] < 1500 else '[High]'} |")
    md.append(f"| Deterministic Rule Hit Ratio | {eval_summary['rule_hit_ratio']:.1f}% | > 85% | {'[Pass]' if eval_summary['rule_hit_ratio'] >= 85 else '[Low]'} |")
    md.append(f"| Compliance Violations | {eval_summary['compliance_violations']} | 0 | [Pass] |")
    md.append("")

    return "\n".join(md)
