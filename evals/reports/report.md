# Recoup — Evaluation Report

> Autonomous Revenue Recovery Agent — Held-Out Test Set Results

---

## Executive Summary

- **Total Events Evaluated:** 104
- **Total Revenue at Risk:** ₹745,090.99
- **Total Revenue Recovered:** **₹100,278.46** (13.5%)
- **Lift over Naive Retry Baseline:** **+₹3,477.38** (+3.6%)
- **Deterministic Rule Hit Ratio:** **93.3%** (97/104)
- **Classification Accuracy:** **49.0%**
- **Compliance Violations:** **0** (Pass)
- **p50 Latency:** **0.0ms** | **p95 Latency:** **16.0ms**

---

## 1. Baseline Performance Comparison

| Approach | Revenue Recovered (₹) | Recovery Rate (%) | Lift vs. Baseline |
|---|---|---|---|
| **Do Nothing** | ₹0.00 | 0.0% | Baseline |
| **Naive Retry-Everything** | ₹96,801.08 | 13.0% | +₹96,801.08 |
| **Recoup Agent (Full Pipeline)** | **₹100,278.46** | **13.5%** | **+₹3,477.38 (+3.6%)** |

---

## 2. Root Cause Classifier Performance

| Root Cause Category | Support | Precision | Recall | F1 Score |
|---|---|---|---|---|
| `authentication_failed` | 9 | 1.00 | 1.00 | 1.00 |
| `checkout_friction` | 0 | 0.00 | 0.00 | 0.00 |
| `expired_instrument` | 1 | 1.00 | 1.00 | 1.00 |
| `insufficient_funds` | 4 | 0.50 | 1.00 | 0.67 |
| `invalid_details` | 5 | 1.00 | 1.00 | 1.00 |
| `issuer_unavailable` | 4 | 0.57 | 1.00 | 0.73 |
| `limit_exceeded` | 5 | 1.00 | 1.00 | 1.00 |
| `mandate_issue` | 8 | 0.53 | 1.00 | 0.70 |
| `network_error` | 4 | 0.67 | 1.00 | 0.80 |
| `risk_declined` | 4 | 1.00 | 1.00 | 1.00 |
| `unknown` | 60 | 1.00 | 0.12 | 0.21 |

---

## 3. System Latency & Provider Distribution

| Metric | Value | Target | Status |
|---|---|---|---|
| p50 Latency (Event → Action) | 0.0 ms | < 500 ms | [Pass] |
| p95 Latency (Event → Action) | 16.0 ms | < 1500 ms | [Pass] |
| Deterministic Rule Hit Ratio | 93.3% | > 85% | [Pass] |
| Compliance Violations | 0 | 0 | [Pass] |
