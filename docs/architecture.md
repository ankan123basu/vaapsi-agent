# 🏗 Vaapsi (वापसी) — Technical Architecture Specification

> **"Jo paisa gaya, wapas aayega."**  
> *Autonomous, Explainable, Compliance-Bounded Revenue Recovery Agent for Indian Merchants*

---

## 📑 Table of Contents
- [1. System-Level Architecture](#1-system-level-architecture)
- [2. 8-Node LangGraph State Machine Pipeline](#2-8-node-langgraph-state-machine-pipeline)
- [3. Hybrid Classifier & Suppression Engine](#3-hybrid-classifier--suppression-engine)
- [4. Webhook Ingestion & Idempotency Pipeline](#4-webhook-ingestion--idempotency-pipeline)
- [5. Component Interactions & Data Schema](#5-component-interactions--data-schema)

---

## 1. System-Level Architecture

Vaapsi operates as a decoupled microservices system consisting of a **FastAPI Agent Service Core**, an **8-Node LangGraph StateGraph Execution Engine**, external **LLM Providers (Groq & Gemini)**, **Razorpay Payment API Integration**, **gTTS Multi-Language Speech Synthesis**, a **Java 17 SHA-256 Cryptographic Audit Ledger Microservice**, and a **React 19 Neobrutalist Web Dashboard**.

```mermaid
graph TD
    subgraph Ingestion ["1. Event Ingestion Layer"]
        RZP["Razorpay Webhook API"] -->|POST /api/webhooks/razorpay| VERIFY["HMAC-SHA256 Signature Verifier"]
        SYN["Synthetic Batch Generator"] -->|POST /api/process-batch| STREAM["SSE Stream Handler"]
        VERIFY --> DUP["SQLite Idempotency Store"]
    end

    subgraph Core ["2. LangGraph Agent Core"]
        DUP -->|New Event| DAG["LangGraph 8-Node DAG Engine"]
        STREAM -->|Event Batch| DAG
    end

    subgraph Classifiers ["3. Hybrid Classifier & Suppression Engine"]
        DAG -->|Node 2: Diagnoser| RULES["Deterministic Rules Engine - 0.4ms"]
        RULES -->|Ambiguous Code| GROQ["Primary LLM: Groq - openai/gpt-oss-120b"]
        GROQ -->|Failure Fallback| GEMINI["Fallback LLM: Gemini - gemini-2.5-flash"]
        DAG -->|Node 3: Suppression| SUPP["Nuisance-Suppression Scorer - Self-Resolution Prob > 55%"]
    end

    subgraph Actions ["4. Execution & Governance Layer"]
        SUPP -->|High Probability > 55%| REPORTERS["Node 8: Reporter (Monitor Only, No Contact)"]
        SUPP -->|Active Recovery| STRAT["Node 4: Strategist - Policy Table"]
        STRAT -->|Node 5: Guardrail Gate| GATE["Compliance Gate - DND / Retries / INR 5,000 Threshold"]
        GATE -->|Needs Approval| QUEUE["Human Approval Queue"]
        GATE -->|Approved| EXEC["Node 6: Executor"]
        EXEC -->|payment_link| RZP_API["Razorpay Payment Links API - rzp.io"]
        EXEC -->|voice| GTTS["gTTS Speech Synthesizer - en, hi, hinglish, ta, bn"]
        EXEC -->|Node 7: Auditor| JAVA_LEDGER["Java 17 Audit Ledger Microservice - Port 8088 SHA-256 Hash Chain"]
    end

    subgraph Presentation ["5. Frontend Presentation Layer"]
        JAVA_LEDGER -->|Node 8: Reporter| DB[("SQLite Audit Database")]
        DB -->|REST / SSE| DASH["React 19 Neobrutalist Dashboard"]
        DASH --> THREE["MoltenHero3D WebGL Canvas"]
        DASH --> TRACE["3D Decision-Trace Viewer"]
        JAVA_LEDGER -->|GET /verify-chain| DASH
    end
```

---

## 2. 8-Node LangGraph State Machine Pipeline

The agent core is structured as a **LangGraph StateGraph** operating on an immutable `RecoveryCase` state object across 8 sequential execution nodes with conditional routing.

```mermaid
graph LR
    subgraph LangGraph DAG Pipeline
        N1["1. Detector<br/><i>Payload Ingestion</i>"] --> N2["2. Diagnoser<br/><i>Hybrid Rules + Groq LLM</i>"]
        N2 --> N3["3. Suppression<br/><i>Self-Resolution Scorer</i>"]
        N3 -->|Suppressed > 55%| N8["8. Reporter<br/><i>Monitor Only</i>"]
        N3 -->|Active| N4["4. Strategist<br/><i>Policy Matrix Lookup</i>"]
        N4 --> N5["5. Guardrail Gate<br/><i>Compliance Boundary</i>"]
        N5 -->|Approved| N6["6. Executor<br/><i>Razorpay API / gTTS</i>"]
        N5 -->|Needs Approval| QUEUE["Human Approval Queue"]
        QUEUE -->|Approved| N6
        N6 --> N7["7. Auditor<br/><i>SQLite + Java SHA-256 Ledger</i>"]
        N7 --> N8["8. Reporter<br/><i>Batch Metrics Aggregation</i>"]
    end
```

### Pipeline Node Roles:

| Node | Name | Latency Profile | Primary Responsibility |
|---|---|---|---|
| **1** | `Detector` | `<0.1ms` | Ingests event payload, validates customer data, calculates total revenue at risk |
| **2** | `Diagnoser` | `0.4ms` (Rule) / `~780ms` (LLM) | Classifies root cause using Rules Engine $\rightarrow$ Groq LLM fallback |
| **3** | `Suppression Scorer` | `<0.1ms` | Calculates self-resolution probability based on decline cause, retry count, and attempt number |
| **4** | `Strategist` | `<0.1ms` | Queries deterministic policy matrix for action, channel, and delay hours |
| **5** | `Guardrail Gate` | `<0.1ms` | Enforces DND hours (9 PM–8 AM IST), 3-retry cap, opt-outs, ₹5,000 threshold |
| **6** | `Executor` | `<0.1ms` (or API time) | Creates live Razorpay test payment link (`rzp.io`) or synthesizes gTTS audio |
| **7** | `Auditor` | `<0.1ms` | Writes immutable node-by-node execution trail into SQLite audit ledger & dispatches to Java SHA-256 ledger |
| **8** | `Reporter` | `<0.1ms` | Aggregates batch metrics and emits Server-Sent Events (SSE) |

---

## 3. Hybrid Classifier Algorithm Flow

Root cause classification combines high-speed deterministic pattern matching with Groq LLM fallback and zero-unknown fallback policy mapping.

```mermaid
flowchart TD
    A["Incoming Transaction Event"] --> B{"Rules Engine Match?<br/>Regex and Bank Error Codes"}
    B -->|"Yes - 91.3% of cases"| C["Return Rule Classification<br/>Latency: 0.4ms<br/>Provider: deterministic/rules_engine"]
    B -->|"No - 8.7% of cases"| D["Invoke Primary LLM: Groq<br/>Model: openai/gpt-oss-120b"]
    D --> E{"Groq Success?"}
    E -->|"Yes"| F["Extract Structured JSON<br/>Latency: ~780ms<br/>Provider: groq/openai/gpt-oss-120b"]
    E -->|"No"| G["Invoke Fallback LLM: Gemini<br/>Model: gemini-2.5-flash"]
    G --> H{"Gemini Success?"}
    H -->|"Yes"| I["Extract Structured JSON<br/>Provider: gemini/gemini-2.5-flash"]
    H -->|"No"| J["Apply Fallback Policy<br/>mandate_issue / issuer_unavailable"]
    F --> K{"Root Cause is unknown?"}
    I --> K
    J --> K
    K -->|"Yes"| L["Zero-Unknown Policy Resolver<br/>Map to issuer_unavailable / checkout_friction"]
    K -->|"No"| M["Final Classified Root Cause"]
    L --> M
```

---

## 4. Webhook Ingestion & Idempotency Pipeline

To prevent double recovery attempts or duplicate customer contacts from webhook retries, incoming payloads are processed through cryptographic signature verification and SQLite event deduplication.

```mermaid
sequenceDiagram
    autonumber
    participant RZP as Razorpay Gateway
    participant SIG as Signature Verifier
    participant IDEM as Idempotency Engine
    participant DB as SQLite DB
    participant AGENT as LangGraph Pipeline

    RZP->>SIG: POST /api/webhooks/razorpay (x-razorpay-signature)
    SIG->>SIG: Compute HMAC-SHA256(payload, secret)
    alt Invalid Signature
        SIG-->>RZP: 400 Bad Request (Invalid Signature)
    else Valid Signature
        SIG->>IDEM: Forward Verified Event
        IDEM->>IDEM: Compute SHA-256 Event Fingerprint
        IDEM->>DB: Check Fingerprint in Database
        alt Fingerprint Exists (Duplicate Event)
            DB-->>IDEM: Event Record Found
            IDEM-->>RZP: 200 OK (Duplicate Ignored / Idempotent No-Op)
        else Fingerprint New
            IDEM->>DB: Insert Fingerprint Record
            IDEM->>AGENT: Trigger 8-Node LangGraph StateMachine
            AGENT-->>RZP: 200 OK (Event Enqueued & Processed)
        end
    end
```

---

## 5. Component Interactions & Data Schema

The `RecoveryCase` state schema encapsulates full lifecycle state:

```json
{
  "case_id": "case_f3155ea9e4b5",
  "event_id": "evt_proof_b5d9c900",
  "event_type": "payment_failed",
  "amount_at_risk": 2500.0,
  "currency": "INR",
  "root_cause": "invalid_details",
  "root_cause_confidence": 1.0,
  "diagnosis_method": "rule",
  "self_resolution_probability": 0.0,
  "contact_suppressed": false,
  "suppression_reasoning": "Score 0.00 <= threshold 0.55",
  "recovery_channel": "payment_link",
  "recovery_action": "payment_link",
  "guardrail_status": "approved",
  "execution_status": "success",
  "case_status": "executed",
  "recovery_amount": 2500.0
}
```
