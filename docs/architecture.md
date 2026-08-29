# 🏗 Vaapsi (वापसी) — Technical Architecture Specification

> **"Jo paisa gaya, wapas aayega."**  
> *Autonomous, Explainable, Compliance-Bounded Revenue Recovery Agent for Indian Merchants*

---

## 📑 Table of Contents
- [1. System-Level Architecture](#1-system-level-architecture)
- [2. 7-Node LangGraph State Machine Pipeline](#2-7-node-langgraph-state-machine-pipeline)
- [3. Hybrid Classifier Algorithm Flow](#3-hybrid-classifier-algorithm-flow)
- [4. Webhook Ingestion & Idempotency Pipeline](#4-webhook-ingestion--idempotency-pipeline)
- [5. Component Interactions & Data Schema](#5-component-interactions--data-schema)

---

## 1. System-Level Architecture

Vaapsi operates as a decoupled microservices system consisting of a **FastAPI Agent Service Core**, a **LangGraph StateGraph Execution Engine**, external **LLM Providers (Groq & Gemini)**, **Razorpay Payment API Integration**, **gTTS Multi-Language Speech Synthesis**, and a **React 19 Neobrutalist Web Dashboard**.

```mermaid
graph TD
    subgraph Ingestion ["1. Event Ingestion Layer"]
        RZP["Razorpay Webhook API"] -->|POST /api/webhooks/razorpay| VERIFY["HMAC-SHA256 Signature Verifier"]
        SYN["Synthetic Batch Generator"] -->|POST /api/process-batch| STREAM["SSE Stream Handler"]
        VERIFY --> DUP["SQLite Idempotency Store"]
    end

    subgraph Core ["2. LangGraph Agent Core"]
        DUP -->|New Event| DAG["LangGraph 7-Node DAG Engine"]
        STREAM -->|Event Batch| DAG
    end

    subgraph Classifiers ["3. Hybrid Classifier Engine"]
        DAG -->|Node 2: Diagnoser| RULES["Deterministic Rules Engine - 0.4ms"]
        RULES -->|Ambiguous Code| GROQ["Primary LLM: Groq - openai/gpt-oss-120b"]
        GROQ -->|Failure Fallback| GEMINI["Fallback LLM: Gemini - gemini-2.5-flash"]
    end

    subgraph Actions ["4. Execution & Governance Layer"]
        DAG -->|Node 4: Guardrail Gate| GATE["Compliance Gate - DND / Retries / INR 5,000 Threshold"]
        GATE -->|Needs Approval| QUEUE["Human Approval Queue"]
        GATE -->|Approved| EXEC["Node 5: Executor"]
        EXEC -->|payment_link| RZP_API["Razorpay Payment Links API - rzp.io"]
        EXEC -->|voice| GTTS["gTTS Speech Synthesizer - en, hi, hinglish, ta, bn"]
    end

    subgraph Presentation ["5. Frontend Presentation Layer"]
        DAG -->|Node 7: Reporter| DB[("SQLite Audit Database")]
        DB -->|REST / SSE| DASH["React 19 Neobrutalist Dashboard"]
        DASH --> THREE["MoltenHero3D WebGL Canvas"]
        DASH --> TRACE["3D Decision-Trace Viewer"]
    end
```

---

## 2. 7-Node LangGraph State Machine Pipeline

The agent core is structured as a **LangGraph StateGraph** operating on an immutable `RecoveryCase` state object across 7 sequential execution nodes.

```mermaid
graph LR
    subgraph LangGraph DAG Pipeline
        N1["1. Detector<br/><i>Risk and Payload Ingestion</i>"] --> N2["2. Diagnoser<br/><i>Hybrid Rules + Groq LLM</i>"]
        N2 --> N3["3. Strategist<br/><i>Policy Matrix Lookup</i>"]
        N3 --> N4["4. Guardrail Gate<br/><i>Compliance Boundary Check</i>"]
        N4 -->|Approved| N5["5. Executor<br/><i>Razorpay API / gTTS</i>"]
        N4 -->|Needs Approval| QUEUE["Human Approval Queue"]
        QUEUE -->|Approved| N5
        N5 --> N6["6. Auditor<br/><i>SQLite Ledger Logging</i>"]
        N6 --> N7["7. Reporter<br/><i>Batch Metrics Aggregation</i>"]
    end
```

### Pipeline Node Roles:

| Node | Name | Latency Profile | Primary Responsibility |
|---|---|---|---|
| **1** | `Detector` | `<0.1ms` | Ingests event, validates payload, calculates total revenue at risk |
| **2** | `Diagnoser` | `0.4ms` (Rule) / `~1040ms` (LLM) | Classifies root cause using Rules Engine $\rightarrow$ Groq LLM fallback |
| **3** | `Strategist` | `<0.1ms` | Queries deterministic policy matrix for action, channel, and delay hours |
| **4** | `Guardrail Gate` | `<0.1ms` | Enforces DND hours (9 PM–8 AM IST), 3-retry cap, opt-outs, ₹5,000 threshold |
| **5** | `Executor` | `<0.1ms` (or API time) | Creates live Razorpay test payment link (`rzp.io`) or synthesizes gTTS audio |
| **6** | `Auditor` | `<0.1ms` | Appends immutable audit entry to SQLite database |
| **7** | `Reporter` | `<0.1ms` | Aggregates batch metrics and emits Server-Sent Events (SSE) |

---

## 3. Hybrid Classifier Algorithm Flow

Root cause classification combines high-speed deterministic pattern matching with Groq LLM fallback and zero-unknown fallback policy mapping.

```mermaid
flowchart TD
    A["Incoming Transaction Event"] --> B{"Rules Engine Match?<br/>Regex and Bank Error Codes"}
    B -->|"Yes - 92% of cases"| C["Return Rule Classification<br/>Latency: 0.4ms<br/>Provider: deterministic/rules_engine"]
    B -->|"No - 8% of cases"| D["Invoke Primary LLM: Groq<br/>Model: openai/gpt-oss-120b"]
    D --> E{"Groq Success?"}
    E -->|"Yes"| F["Extract Structured JSON<br/>Latency: ~1040ms<br/>Provider: groq/openai/gpt-oss-120b"]
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
            IDEM->>AGENT: Trigger 7-Node LangGraph StateMachine
            AGENT-->>RZP: 200 OK (Event Enqueued & Processed)
        end
    end
```

---

## 5. Component Interactions & Data Schema

### `RecoveryCase` Shared State Schema:

```typescript
interface RecoveryCase {
  case_id: string;                // e.g. "case_c719ce8255aa"
  event_type: string;             // "payment_failed" | "mandate_failed" | "checkout_abandoned"
  decline_reason_raw: string;     // e.g. "DO_NOT_HONOR" | "3DS_TIMEOUT"
  amount_at_risk: number;         // Amount in INR
  currency: string;               // "INR"
  customer_name: string;          // Customer name
  customer_email: string;         // Customer email
  customer_phone: string;         // Customer contact number
  root_cause: string;             // Classified root cause
  root_cause_confidence: number;  // 0.0 - 1.0
  diagnosis_method: "rule" | "llm_fallback";
  diagnosis_provider: string;     // e.g. "groq/openai/gpt-oss-120b"
  diagnosis_latency_ms: number;   // Execution latency in ms
  recovery_channel: string;       // "payment_link" | "voice" | "email" | "sms"
  recovery_action: string;        // "send_payment_link" | "voice_call"
  message_content: string;        // Drafted recovery message
  guardrail_status: "approved" | "blocked" | "pending_approval";
  guardrail_violations: string[]; // Active intervention notes
  execution_status: "success" | "failed";
  execution_result: object;       // Razorpay link ID / gTTS audio payload
  audit_trail: AuditEntry[];      // Full reasoning chain ledger
}
```
