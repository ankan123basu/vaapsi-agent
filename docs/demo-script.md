# Recoup — Demo Script (5-Minute Pitch Video)

> Shot list for the pitch video. Fill in actual numbers after Phase 5 eval run.

## Shot List

### 1. Hook (0:00–0:30)
- Open on the live recovery ticker showing ₹ recovered in real-time
- One-liner: "Recoup is an autonomous agent that finds revenue leaking out of
  your payment funnel, diagnoses why, recovers it, and proves the numbers."

### 2. The Problem (0:30–1:00)
- Quick stats: X% of payments fail, Y% of checkouts are abandoned
- Show the synthetic data: 300+ realistic events with noisy data
- "Most recovery tools retry blindly. Recoup diagnoses first."

### 3. The Agent Pipeline (1:00–2:30)
- Click a recovered case in the dashboard
- Walk through the decision trace: Detector → Diagnoser → Strategist → Gate → Executor
- Highlight: "87% resolved by deterministic rules, 13% needed LLM judgment"
- Show the Groq latency: "Classification in 340ms"
- Show a case where the agent chose NOT to act (guardrail block)

### 4. Compliance Panel (2:30–3:30)
- "0 compliance violations across N cases"
- Walk through the four guardrails: retry cap, DND, opt-out, human approval
- Show the human approval queue
- "This is what a fintech company would actually need to deploy this."

### 5. Eval Report (3:30–4:30)
- Show the generated eval report
- Baseline comparison: do-nothing vs. naive retry vs. Recoup
- Confusion matrix for root-cause classifier
- p50/p95 latency numbers

### 6. What Broke (4:30–5:00)
- The duplicate webhook story (ADR-0002)
- Show idempotent handling: duplicate event → safe no-op in the log
- "We designed this failure in deliberately, then solved it properly."

## Production Notes
- Record at 1080p, good lighting
- Use actual dashboard with real eval data (not placeholders)
- Keep energy focused, not rushed
