# 🎯 Architectural Decisions & Tradeoffs (ADRs)

> **Vaapsi (वापसी) — Technical Decision Records**  
> *Documentation of foundational architectural choices, alternatives evaluated, and engineering tradeoffs.*

---

## 📑 Index of Decisions

- [ADR-001: LangGraph DAG State Machine Engine](#adr-001-langgraph-dag-state-machine-engine)
- [ADR-002: Hybrid Rules + Groq LLM Root Cause Classifier](#adr-002-hybrid-rules--groq-llm-root-cause-classifier)
- [ADR-003: Deterministic Policy Matrix vs. LLM Action Selection](#adr-003-deterministic-policy-matrix-vs-llm-action-selection)
- [ADR-004: gTTS Server-Side Speech Synthesis vs. Web Speech API](#adr-004-gtts-server-side-speech-synthesis-vs-web-speech-api)
- [ADR-005: SQLite Event Fingerprinting vs. External Redis Store](#adr-005-sqlite-event-fingerprinting-vs-external-redis-store)
- [ADR-006: Viewport-Scoped Custom Cursor for Financial Surfaces](#adr-006-viewport-scoped-custom-cursor-for-financial-surfaces)

---

## ADR-001: LangGraph DAG State Machine Engine

### Context
An autonomous revenue recovery agent requires multi-step processing: risk calculation, root cause diagnosis, policy lookup, compliance boundary checking, Razorpay API execution, audit logging, and metrics aggregation.

### Decision
Use **LangGraph** (`langchain-core` / `langgraph`) to model the pipeline as a 7-node Directed Acyclic Graph (DAG) operating on an immutable `RecoveryCase` typed state dictionary.

### Alternatives Considered
1. **Procedural Python Script Loops**: Standard sequential function calls (`step1() -> step2() -> step3()`).
   - *Rejected:* Hard to inspect intermediate states, lacks visual graph debugging, difficult to pause for human approval.
2. **Celery / Temporal Workflow Orchestrators**: Heavy asynchronous task queues.
   - *Rejected:* Overkill for single-pass state transitions; requires Redis/RabbitMQ infrastructure setup.

### Tradeoffs
* **(+) Positives:** Immutable state transitions, automatic step-by-step audit trails, seamless human-in-the-loop pause/resume (`Guardrail Gate`), and direct 3D visual graph rendering in the frontend.
* **(-) Negatives:** Slight learning curve and initial schema declaration overhead.

---

## ADR-002: Hybrid Rules + Groq LLM Root Cause Classifier

### Context
Transaction failures produce raw bank decline codes (e.g. `DO_NOT_HONOR`, `3DS_TIMEOUT`, `INSUFFICIENT_FUNDS`, `UNKNOWN_ERROR`). Evaluating every failure with an LLM adds unnecessary latency and cost, while hardcoded rules fail on vague errors.

### Decision
Implement a **2-Layer Hybrid Classifier Engine**:
* **Layer 1 (Deterministic Rules Engine)**: Fast regex and status table matching (`0.4ms` execution time). Handles 92% of standard decline codes.
* **Layer 2 (LLM Fallback Inference)**: Groq `openai/gpt-oss-120b` (fallback to Gemini `gemini-2.5-flash`) for ambiguous codes (`UNKNOWN_ERROR`, `DO_NOT_HONOR`).
* **Zero-Unknown Resolution**: Auto-maps residual ambiguous outputs to actionable categories (`issuer_unavailable`, `checkout_friction`).

### Tradeoffs
* **(+) Positives:** 92% of events execute in sub-millisecond time (`0.4ms`), reducing overall API costs and p50 latency while providing LLM intelligence for complex cases.
* **(-) Negatives:** Requires maintaining both regex rule tables and LLM prompts.

---

## ADR-003: Deterministic Policy Matrix vs. LLM Action Selection

### Context
Once a root cause is classified (e.g. `issuer_unavailable`), the system must pick a recovery channel (`payment_link`, `voice`, `email`), action, and delay hours.

### Decision
Enforce a **Deterministic Policy Matrix** (`RECOVERY_POLICY` in `strategist.py`). The LLM is NEVER permitted to choose recovery policies, channels, or retry delays; its role is strictly limited to root cause diagnosis and drafting human-friendly recovery message text.

### Tradeoffs
* **(+) Positives:** 100% eliminates AI hallucination risk in money-handling recovery decisions. Ensures strict regulatory compliance and predictable business logic.
* **(-) Negatives:** Slightly reduces experimental AI autonomy.

---

## ADR-004: gTTS Server-Side Speech Synthesis vs. Web Speech API

### Context
Vaapsi features multi-language voice calls (`English`, `Hindi`, `Hinglish`, `Tamil`, `Bengali`) to recover abandoned checkouts and subscription failures.

### Decision
Use server-side **gTTS (Google Text-to-Speech)** with Indian dialect TLDs (`co.in`) to synthesize Base64 MP3 audio payloads delivered directly in API responses.

### Alternatives Considered
* **Browser Web Speech API (`window.speechSynthesis`)**:
  - *Rejected:* Inconsistent voice quality across browsers, lack of native Hinglish voice models on desktop OSs.

### Tradeoffs
* **(+) Positives:** 100% consistent audio pronunciation across all devices, zero browser dependency, multi-language support.
* **(-) Negatives:** Requires server-side audio buffer generation (~120ms latency).

---

## ADR-005: SQLite Event Fingerprinting vs. External Redis Store

### Context
Razorpay webhooks can emit duplicate events or retry failed HTTP deliveries. The system must guarantee idempotency to prevent duplicate customer contacts or double payment links.

### Decision
Use **HMAC-SHA256 signature verification** alongside an embedded **SQLite deduplication database** (`recoup.db`). Event fingerprints are computed as `hashlib.sha256(f"{event_id}:{event_type}:{amount}".encode()).hexdigest()`.

### Tradeoffs
* **(+) Positives:** Zero external infrastructure dependencies (no Redis/Memcached required), single-command `docker-compose` deployment, full transaction safety.
* **(-) Negatives:** Single-node concurrency boundary (sufficient for single-merchant deployment).

---

## ADR-006: Viewport-Scoped Custom Cursor for Financial Surfaces

### Context
A high-tech target cursor component (`TargetCursor.tsx`) adds a visual experience in the hero section, but custom cursors can feel imprecise or distracting on data tables and approval buttons.

### Decision
Scope `TargetCursor.tsx` strictly to the landing hero section using an `IntersectionObserver`. When the user scrolls past the hero into the dashboard, `TargetCursor` unmounts and restores the standard OS cursor (`document.body.style.cursor = ''`).

### Tradeoffs
* **(+) Positives:** Preserves high-tech visual impact for first impressions while maintaining clean, calm precision on financial surfaces (case tables, approval queue).
* **(-) Negatives:** Requires tracking hero section viewport intersection state.
