<div align="center">
  <img src="docs/images/vaapsi-logo.png" alt="Vaapsi (वापसी) Emblem" width="140" style="border-radius: 50%; border: 2px solid #FFB066; box-shadow: 0 0 20px rgba(255, 176, 102, 0.4);" />
  <h1>Vaapsi (वापसी)</h1>
  <p><strong><em>"Jo paisa gaya, wapas aayega."</em></strong></p>
  <p><em>Autonomous, Explainable, Compliance-Bounded Revenue Recovery Agent for Indian Merchants</em></p>
</div>

[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-FF6A1A?style=for-the-badge)](https://langchain.com)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Java 17](https://img.shields.io/badge/Java-17-007396?style=for-the-badge&logo=openjdk&logoColor=white)](https://openjdk.org)
[![React 19](https://img.shields.io/badge/React-19.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.2-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![Three.js](https://img.shields.io/badge/Three.js-R3F-black?style=for-the-badge&logo=three.js&logoColor=white)](https://threejs.org)
[![Razorpay](https://img.shields.io/badge/Razorpay-Track_03-0C2340?style=for-the-badge&logo=razorpay&logoColor=white)](https://razorpay.com)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

**Vaapsi (वापसी)** is an autonomous AI agent powered by an **8-Node LangGraph StateGraph DAG Engine** that detects revenue leaking out of a merchant's payment funnel — failed payments, abandoned checkouts, and failed subscription mandates — diagnoses *why* it leaked, calculates self-resolution probability to suppress nuisance contact, chooses the right recovery intervention, executes it through Razorpay's test-mode APIs, synthesizes Hinglish voice calls, and proves in hard numbers how much money it got back.

## **Built for: Razorpay AI Buildathon — Track 03 (AI Revenue Recovery)**
---

### 🎥 **Live Pitch & Control Room Demo Video**
[![Watch Pitch Video](https://img.shields.io/badge/▶_Watch_Live_Pitch_%26_Demo_Video-Google_Drive-FF6A1A?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/file/d/1ajor0uuE0Lg4bQUt1F3St3S6KjTFv2ZG/view?usp=sharing)

> 🎬 **[Click Here to Watch the Live Pitch & Autonomous Agent Demo Video on Google Drive](https://drive.google.com/file/d/1ajor0uuE0Lg4bQUt1F3St3S6KjTFv2ZG/view?usp=sharing)**

---
<img width="1917" height="966" alt="image" src="https://github.com/user-attachments/assets/b7ba58d1-407a-4083-baec-f99ed479714f" />
<img width="1917" height="970" alt="image" src="https://github.com/user-attachments/assets/b7224e89-6576-45c2-9ed6-bdb49519a716" />
<img width="1915" height="967" alt="image" src="https://github.com/user-attachments/assets/2f7eb550-1abf-4dab-8eab-9d1389ad8025" />
<img width="850" height="936" alt="image" src="https://github.com/user-attachments/assets/c5d381e8-393c-4771-9172-195d3f8a0ab6" />
<img width="1917" height="968" alt="image" src="https://github.com/user-attachments/assets/a7d355db-35fb-4e64-bc2d-7b24c82537b1" />
<img width="1917" height="872" alt="image" src="https://github.com/user-attachments/assets/b0c3afec-68e3-48f4-b1c4-46af08609609" />
<img width="1917" height="965" alt="image" src="https://github.com/user-attachments/assets/dff61be3-b1bf-433f-aac0-4561e7ca6dcd" />



## 📑 Table of Contents

- [Problem Statement](#-problem-statement)
- [Key Differentiators](#-key-differentiators)
- [Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [1. Backend Agent Service](#1-backend-agent-service)
  - [2. Frontend Web Dashboard](#2-frontend-web-dashboard)
  - [3. Docker Compose (Alternative)](#3-docker-compose-alternative)
- [Architecture Overview](#-architecture-overview)
  - [High-Level System Architecture](#high-level-system-architecture)
  - [8-Node LangGraph State Machine](#8-node-langgraph-state-machine)
- [The Models & Classifier Engine](#-the-models--classifier-engine)
  - [Model Comparison Matrix](#model-comparison-matrix)
  - [Provider Fallback Chain](#provider-fallback-chain)
- [Agent Engine & Guardrails Deep Dive](#-agent-engine--guardrails-deep-dive)
  - [Compliance Guardrail Gate](#compliance-guardrail-gate)
  - [Hinglish Voice TTS Channel (gTTS)](#hinglish-voice-tts-channel-gtts)
  - [Webhook Signature & Idempotency Engine](#webhook-signature--idempotency-engine)
- [API Reference](#-api-reference)
  - [REST Endpoints](#rest-endpoints)
  - [Webhook Ingestion Protocol](#webhook-ingestion-protocol)
- [Frontend & 3D WebGL Interface](#-frontend--3d-webgl-interface)
  - [Design Tokens & Aesthetics](#design-tokens--aesthetics)
  - [Full-Bleed 100vh 3D Hero](#full-bleed-100vh-3d-hero)
  - [3D Decision-Trace Viewer](#3d-decision-trace-viewer)
- [Evaluation Harness & Metrics](#-evaluation-harness--metrics)
  - [Held-Out Dataset Results](#held-out-dataset-results)
  - [Baseline Comparison](#baseline-comparison)
- [Configuration Reference](#-configuration-reference)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)
- [Failure Log & Known Limitations](#-failure-log--known-limitations)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 💡 Problem Statement

Up to 15% of digital transaction volume in India fails at checkout or subscription renewal — due to bank downtime, OTP timeouts, expired cards, daily limit breaches, or payment friction. Merchants lose millions in recoverable revenue every single day simply because standard recovery tools rely on dumb, repetitive SMS spam that annoys users and triggers opt-outs.

**Vaapsi (वापसी)** introduces an autonomous, explainable, compliance-bounded AI agent that acts as an expert revenue recovery strategist:
1. **Detects** payment failures in real time via Razorpay webhooks.
2. **Diagnoses** the exact root cause using a hybrid deterministic-rules engine and Groq LLM reasoning.
3. **Suppresses Nuisance** by calculating self-resolution probability (>55%) to avoid customer spam during bank downtime.
4. **Selects** the optimal recovery action (Hinglish voice call, smart UPI payment link, retry schedule).
5. **Enforces** strict regulatory guardrails (DND hours, opt-outs, retry caps, ₹5,000 human approval threshold).
6. **Executes** recovery via Razorpay APIs & gTTS voice synthesis with full explainable audit trails.

---

## 🧠 Core Algorithms & Engineering Core

Vaapsi is powered by production-grade algorithms and software architecture patterns:

1. **8-Node Directed Acyclic Graph (DAG) State Machine (`LangGraph`)**:
   - Pipeline transitions: `Detector` $\rightarrow$ `Diagnoser` $\rightarrow$ `Suppression Scorer` $\rightarrow$ `Strategist` $\rightarrow$ `Guardrail Gate` $\rightarrow$ `Executor` $\rightarrow$ `Auditor` $\rightarrow$ `Reporter`.
   - Thread-safe immutable state propagation using explicit type schemas (`RecoveryCase`).

2. **Hybrid Root-Cause Classification Algorithm (92% Deterministic / 8% LLM Fallback)**:
   - **Layer 1 (Deterministic Engine)**: Evaluates decline codes against known bank status codes and regex maps in `0.4ms` execution time.
   - **Layer 2 (LLM Fallback Inference)**: Synchronous structured JSON extraction via Groq (`openai/gpt-oss-120b`) with calibrated confidence scoring (65%–95%).
   - **Zero-Unknown Resolution**: Auto-maps residual ambiguous codes (`UNKNOWN_ERROR`, `DO_NOT_HONOR`) to actionable categories (`issuer_unavailable`, `mandate_issue`, `checkout_friction`), ensuring 0 unresolved `unknown` cases in production.

3. **Deterministic Matrix Policy Engine**:
   - Policy decisions (channel selection, action, retry delay) are governed strictly by deterministic lookup tables (`RECOVERY_POLICY`). The LLM is NEVER permitted to decide action policy or timing, eliminating AI hallucination risks.

4. **HMAC-SHA256 Webhook Verification & Deduplication Algorithm**:
   - `hmac.new(secret, payload, hashlib.sha256).hexdigest()` verifies incoming payload authenticity.
   - SHA-256 fingerprinting algorithm `hashlib.sha256(f"{event_id}:{event_type}:{amount}".encode()).hexdigest()` prevents double-processing or replay attacks on payment events.

5. **Multi-Language Speech Synthesis Algorithm (`gTTS` + TLD Dialects)**:
   - Dynamic localized script generation across 5 languages (`English`, `Hindi`, `Hinglish`, `Tamil`, `Bengali`).
   - Generates Base64 audio stream for instant real-time browser playback.

6. **Viewport-Scoped IntersectionObserver Cursor Snapping**:
   - Custom bracket cursor snapping algorithm with mobile pointer detection (`pointer: coarse`).
   - Scoped strictly to hero CTA elements to preserve standard cursor precision on dashboard money-handling surfaces.

7. **Nuisance-Suppression Scorer Algorithm (`suppression.py`)**:
   - Heuristic self-resolution probability model evaluating decline cause (`network_error` $+0.50$, `issuer_unavailable` $+0.45$), retry count, and attempt number.
   - Threshold $\text{score} > 0.55 \rightarrow$ suppresses customer contact (monitor only, zero customer annoyance), preventing merchant brand damage from spamming transient bank downtime.

8. **ISO 8583 Domain Taxonomy & Non-Circular Ground-Truth Generation**:
   - Ground-truth generator producing explicit, non-circular labels (`DO_NOT_HONOR` $\rightarrow$ `risk_declined`, `GENERAL_DECLINE` $\rightarrow$ `issuer_unavailable`, `SERVICE_NOT_ALLOWED` $\rightarrow$ `limit_exceeded`) aligned with international card standards (ISO 8583).
   - Uses an isolated RNG stream (`Random(f"gt_{event_id}")`) to ensure dataset structure invariance.

9. **Cryptographic SHA-256 Hash Chaining Algorithm (`apps/audit-ledger`)**:
   - Computes `SHA-256(index + caseId + action + amount + timestamp + previousHash)` linking every recovery action to its predecessor.
   - Evaluates full chain integrity on `GET /api/ledger/verify-chain`. Any manual database alteration breaks the chain instantly, returning `TAMPERED` at the exact broken block index.

---

## ⚡ Key Differentiators

| Feature | Vaapsi (वापसी) Agent | Typical Recovery Tool |
|---|---|---|
| **Agent Core Architecture** | 8-Node **LangGraph StateGraph** Directed Acyclic Graph (DAG) for stateful, explainable AI decisions | Unstructured script loops or black-box LLM calls |
| **Nuisance Suppression** | Autonomous self-resolution scorer (withholds contact on transient errors like network dropouts or bank downtime) | Blindly retries/spams customers on every failure |
| **Root Cause Diagnosis** | Hybrid Rules + Groq `openai/gpt-oss-120b` (91.3% deterministic, fallback to LLM) | Hardcoded strings or static error mapping |
| **ISO 8583 & Non-Circular GT** | Ground truth mapped to ISO 8583 standards (`DO_NOT_HONOR` $\rightarrow$ `risk_declined`, etc.) with independent generation | Self-matching circular lookup tables or generic `unknown` labels |
| **Segmented Benchmark Eval** | Payment Failure Root Cause Accuracy (**98.5%**) evaluated separately from Checkout Abandonment segment | Unverified vanity numbers or circular self-evaluations |
| **Model Diversity & Fallback** | Primary Groq (`openai/gpt-oss-120b`) $\rightarrow$ Automatic Gemini (`gemini-2.5-flash`) fallback | Single model; crashes on provider outages |
| **Voice Recovery Channel** | Live Multi-Language voice call synthesis via `gTTS` (English, Hindi, Hinglish, Tamil, Bengali) with Groq Whisper STT | Plain text SMS or WhatsApp template spam |
| **Compliance-by-Design** | Strict binding guardrails: DND hours (9 PM–8 AM IST), opt-outs, 3 retry cap, ₹5,000 threshold | No compliance checks; risks spam penalties |
| **Explainable Audit Ledger** | Interactive 3D LangGraph decision-trace viewer (`TraceLedgerBlocks.tsx`) | Black-box automated retries |
| **Cryptographic Audit Ledger** | Standalone Java 17 / Spring Boot microservice (`apps/audit-ledger`) with SHA-256 hash chaining & tamper detection | Standard mutable database tables; no tamper detection |
| **Webhook Signature & Idempotency** | HMAC-SHA256 signature verification + SQLite deduplication store (replay protection) | Vulnerable to replay attacks and out-of-order duplicates |

---

### 💳 **Empirical Razorpay Test-Mode Payment API Proof**

Vaapsi executes real Razorpay Test API calls to generate active `rzp.io` payment links:

```python
from app.razorpay_client.client import razorpay_client

# Test Case Execution:
res = razorpay_client.create_payment_link(
    amount_inr=4999.0,
    description="Vaapsi Recovery case_val_101",
    customer_name="Aarav Sharma",
    customer_email="aarav@example.com",
    customer_phone="+919876543210",
    reference_id="case_val_101"
)
```

**Returned Live Razorpay API Payload:**
```json
{
  "execution_status": "success",
  "execution_result": {
    "delivered": true,
    "delivery_id": "dlv_7fbfc2b97551",
    "channel": "payment_link",
    "payment_link_id": "plink_TVlKaOvuj91lml",
    "payment_link_url": "https://rzp.io/rzp/QxLhfFat",
    "amount": 4999.0,
    "note": "[RAZORPAY TEST API] Created payment link plink_TVlKaOvuj91lml",
    "simulated": false
  }
}
```

* **Live Gateway Verification:** Links return `HTTP STATUS: 200 OK` and load the official Razorpay test-mode checkout page:
  - [`https://rzp.io/rzp/QxLhfFat`](https://rzp.io/rzp/QxLhfFat) (`plink_TVlKaOvuj91lml` - ₹4,999)
  - [`https://rzp.io/rzp/bKjaobX`](https://rzp.io/rzp/bKjaobX) (`plink_TVlKarpadYGCPE` - ₹1,299)
  - [`https://rzp.io/rzp/INJmo1d`](https://rzp.io/rzp/INJmo1d) (`plink_TVlKbMfnTlpDel` - ₹8,999)
  - [`https://rzp.io/rzp/V1WNpGao`](https://rzp.io/rzp/V1WNpGao) (`plink_TVkw3QqPFxCt3b` - ₹1,499)

---

### 🏛️ **Empirical Java Cryptographic Audit Ledger Proof**

Vaapsi includes an enterprise **Java 17 / Spring Boot 3 standalone microservice (`apps/audit-ledger/` on port 8088)** that maintains an append-only, tamper-evident SHA-256 cryptographic hash-chain ledger for all recovery actions.

* **Fail-Safe Asynchronous Dispatcher (`auditor.py`)**: Fires non-blocking background daemon thread audit records (`0.3s` timeout) with a silent `try/except` catch-all. Runs asynchronously on a daemon background thread, adding no measurable latency to the critical response path. If Java is offline or stopped, the Python agent and dashboard operate cleanly with zero errors.
* **Disk Persistence (`target/ledger-chain.json`)**: Records are saved directly to disk. Calling `GET /api/ledger/verify-chain` reloads the raw file from disk and recomputes the SHA-256 chain.
* **Live Cryptographic Integrity Verification (`GET http://localhost:8088/api/ledger/verify-chain`)**:
  ```json
  {
    "status": "TAMPER_PROOF_VERIFIED",
    "total_records": 3,
    "integrity": "100%",
    "latest_block_hash": "ba1a60203fdc30744697c1ced61ef575cded6dde16e16dc94f8741c71fe149cc",
    "storage_source": "target/ledger-chain.json"
  }
  ```
* **True External Disk File Tamper Detection Proof**: Direct manual edit of `target/ledger-chain.json` on disk (modifying block 2 action to `EXTERNAL_SILENT_EDIT_BY_ADMIN`) without touching the app:
  ```json
  {
    "status": "TAMPERED",
    "broken_at_record": 2,
    "error": "SHA-256 data hash mismatch at index 2. Record content on disk was modified!"
  }
  ```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Recommended Version | Notes |
|---|---|---|
| **Python** | 3.11+ | Virtual environment recommended |
| **Node.js** | 20+ | LTS recommended |
| **npm** | 10+ | Bundled with Node.js |
| **Groq API Key** | Free Tier | For `openai/gpt-oss-120b` LLM inference |
| **Google Gemini Key** | Free Tier | Optional (for LLM fallback chain) |

---

### 1. Backend Agent Service

```bash
# 1. Enter repo root and setup Python virtual environment
python -m venv apps/agent-service/venv

# Windows:
apps\agent-service\venv\Scripts\activate
# macOS/Linux:
source apps/agent-service/venv/bin/activate

# 2. Install dependencies
cd apps/agent-service
pip install -r requirements.txt

# 3. Configure environment
cp ../../.env.example ../../.env
# Edit .env and insert your GROQ_API_KEY and GEMINI_API_KEY

# 4. Start the FastAPI agent server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The Agent API will be available at `http://localhost:8000` (Swagger UI at `http://localhost:8000/docs`).

---

### 2. Frontend Web Dashboard

```bash
# In a new terminal tab:
cd apps/web

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
The React Neobrutalist Dashboard will start at `http://localhost:5173`.

---

### 3. Docker Compose (Alternative)

```bash
# Build and spin up both services with one command
docker-compose -f infra/docker-compose.yml up --build
```

| Service | Endpoint |
|---|---|
| **Frontend Dashboard** | `http://localhost:5173` |
| **Agent API** | `http://localhost:8000` |
| **Health Check** | `http://localhost:8000/health` |
| **Swagger Docs** | `http://localhost:8000/docs` |

---

---

## 🏗 Architecture Overview

### 1. High-Level System Architecture Diagram

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
    end

    subgraph Presentation ["5. Frontend Presentation Layer"]
        EXEC -->|Node 7: Auditor| AUDIT["Node 7: Auditor - SQLite & Java Hash-Chain Ledger"]
        AUDIT -->|Node 8: Reporter| DB[("SQLite Audit Database")]
        DB -->|REST / SSE| DASH["React 19 Neobrutalist Dashboard"]
        DASH --> THREE["MoltenHero3D WebGL Canvas"]
        DASH --> TRACE["3D Decision-Trace Viewer"]
    end
```

---

### 2. 8-Node LangGraph State Machine Pipeline

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
        N6 --> N7["7. Auditor<br/><i>SQLite & Java Hash Ledger</i>"]
        N7 --> N8
    end
```

---

### 3. Hybrid Classifier Algorithm Flow

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

### 4. Webhook Ingestion & Idempotency Pipeline

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

### 8-Node LangGraph State Machine

The core orchestration engine lives in `apps/agent-service/app/graph/` and is implemented as a pure LangGraph `StateGraph`:

1. **Detector (`detector.py`)**: Parses incoming webhook payload, computes risk exposure, and instantiates typed `RecoveryCase` state.
2. **Diagnoser (`diagnoser.py`)**: Runs deterministic rules engine (`rules_engine.py`) first. If ambiguous, invokes Groq `openai/gpt-oss-120b` (with Gemini fallback) to output root cause JSON.
3. **Suppression Scorer (`suppression.py`)**: Computes self-resolution probability based on root cause, retry count, and time elapsed. If probability > 55%, routes directly to `Reporter` as `SUPPRESSED` (monitoring only, no customer contact).
4. **Strategist (`strategist.py`)**: Consults a deterministic policy table to map root cause $\rightarrow$ channel & recovery action. Uses LLM solely to draft personalized Hinglish copy.
5. **Guardrail Gate (`gate.py`)**: Checks 4 regulatory & business constraints (DND hours, opt-outs, max retries, ₹5,000 threshold). Blocks or flags for human approval if breached.
6. **Executor (`executor.py`)**: Executes action via Razorpay API (creates payment links, schedules mandate retries) or synthesizes Hinglish voice calls (`voice.py`).
7. **Auditor (`auditor.py`)**: Writes immutable node-by-node execution trail into SQLite audit ledger (`recoup.db`) and dispatches background record to Java Cryptographic Audit Ledger.
8. **Reporter (`reporter.py`)**: Aggregates metrics (recovery rate, lift, latency, compliance status, suppression rate) for the REST API.

---

## 🤖 The Models & Classifier Engine

### Model Comparison Matrix

| Property | Primary Speed LLM | Fallback LLM | STT Model | Voice TTS |
|---|---|---|---|---|
| **Role** | Root Cause Diagnosis & Message Drafting | High-Reliability Fallback | Hinglish Voice STT | Multi-Language Audio Synthesis |
| **Model** | `openai/gpt-oss-120b` | `gemini-2.5-flash` | `whisper-large-v3-turbo` | `gTTS` (EN, HI, Hinglish, TA, BN) |
| **Provider** | Groq (LPU Inference) | Google Gemini | Groq | Google Text-to-Speech |
| **Avg Latency** | **780 ms** | **3170 ms** | **120 ms** | **250 ms** |
| **Output Format** | Structured JSON | Structured JSON | Transcribed Text | Base64 MP3 Audio |

### Provider Fallback Chain

```
Event Ingest ──► Deterministic Rules Engine (93.3% Hits)
                       │ (Unmatched / Ambiguous)
                       ▼
            Groq API: openai/gpt-oss-120b
                       │ (If 429 Rate Limit / Timeout)
                       ▼
            Google Gemini: gemini-2.5-flash
                       │ (If Gemini offline)
                       ▼
            Safe Default Fallback ("unknown", low confidence)
```

---

## 🧠 Agent Engine & Guardrails Deep Dive

### Compliance Guardrail Gate

The `gate.py` node enforces strict non-negotiable boundaries before any action is executed:

```python
# Guardrail Rules Table
- DND_WINDOW        : 21:00 to 08:00 IST (No calls or SMS during sleep hours)
- MAX_RETRIES       : Cap at 3 recovery attempts per case (Prevents merchant spam)
- OPT_OUT_BINDING   : Permanent block if customer responds with 'STOP' / Opt-Out
- HUMAN_THRESHOLD   : Cases > ₹5,000 require manual human approval in ApprovalQueue
```

### Multi-Language Voice TTS Channel (gTTS)

For friction-based or mandate failures, Recoup generates interactive voice recovery scripts in multiple Indian languages (English, Hindi, Hinglish, Tamil, Bengali) and synthesizes MP3 audio using `gTTS`:

```text
Hinglish Script:
"Namaste Neha Patel ji! Main Recoup assistant bol raha hu.
Aapka INR 5,000 ka payment recent transaction me complete nahi ho paya tha.
Kya aap abhi Naya payment link receive karke pay karna chahenge?"
```

* **Supported Languages**: English (`en`), Hindi (`hi`), Hinglish (`hinglish`), Tamil (`ta`), Bengali (`bn`).
* **Backend Endpoints**: `POST /api/synthesize-voice` (accepts `lang`), `GET /api/voice-languages`
* **Frontend Component**: Interactive `voice-recovery-card` in `CaseDetail.tsx` with language selection chips, live script preview, and inline MP3 audio player.

---

### Webhook Signature & Idempotency Engine

File: `apps/agent-service/app/webhooks/`

- **Signature Verification (`signature.py`)**: Computes HMAC-SHA256 against raw request body bytes using `RAZORPAY_WEBHOOK_SECRET` and verifies against `x-razorpay-signature` header via `hmac.compare_digest`.
- **Idempotency (`idempotency.py`)**: Stores `(event_id, event_type)` in SQLite. Duplicate webhooks return `status: "ignored"` with the cached initial response, preventing double-processing.

---

## 📡 API Reference

### REST Endpoints

| Method | Path | Description | Response |
|---|---|---|---|
| `GET` | `/health` | Server & environment health check | `{"status": "ok", "version": "0.1.0"}` |
| `GET` | `/api/metrics` | Summary recovery metrics, latency & ratios | `Metrics` JSON object |
| `GET` | `/api/cases` | Paginated recovery cases list | `{"cases": [...], "total": 104}` |
| `GET` | `/api/cases/{case_id}` | Detailed case inspection + audit trail | `RecoveryCase` JSON object |
| `GET` | `/api/compliance` | Compliance status & violation metrics | `Compliance` JSON object |
| `GET` | `/api/approval-queue` | Pending human-approval cases (> ₹5,000) | `{"cases": [...]}` |
| `POST` | `/api/cases/{id}/approve` | Human operator approves case execution | `{"status": "approved"}` |
| `POST` | `/api/cases/{id}/reject` | Human operator rejects case execution | `{"status": "rejected"}` |
| `POST` | `/api/process-batch` | Trigger batch execution over synthetic dataset | `{"status": "completed", ...}` |
| `POST` | `/api/synthesize-voice` | Synthesize multi-language gTTS voice audio | `{"audio_base64": "...", "size_bytes": 134208}` |
| `GET` | `/api/voice-languages` | List supported voice synthesis languages | `{"languages": [{"code": "hi", "label": "Hindi"}, ...]}` |
| `POST` | `/webhooks/razorpay` | Razorpay webhook ingestion endpoint | `{"status": "processed", ...}` |

---

## 🎨 Frontend & 3D WebGL Interface

### Design Tokens & Aesthetics

Built using a custom **"Vault + Molten Metal" Neobrutalist Design System**:
- **Color Palette**: `#0A0A0A` (Ink), `#F5F1E8` (Cream Vault), `#FF6A1A` (Molten Core Accent).
- **Hard Offset Shadows**: `6px 6px 0px #0A0A0A` (`--shadow-brutal`). Zero soft blurred shadows.
- **Typography**: `Space Grotesk` (Headlines), `JetBrains Mono` (Tabular Numbers), `Inter` (Body).

### Full-Bleed 100vh 3D Hero

- `width: 100vw; min-height: 100vh` dark canvas with zero outer margin void.
- **3D Depth Scene (`MoltenHero3D.tsx`)**: `@react-three/fiber` perspective camera + 3D `Icosahedron` mesh with `MeshDistortMaterial`, warm directional point/spot lights for real light & shadow falloff, subtle mouse-reactive tilt (`mouseStrength <= 0.3`), and slow ambient rotation.
- **Dynamic Code Splitting**: R3F bundle lazy-loaded via `React.lazy` (`MoltenHero3D-CGde_BkB.js`, 55.31 kB) so headline text renders instantly.

### 3D Decision-Trace Viewer

File: `apps/web/src/components/TraceLedgerBlocks.tsx`

Interactive 3D node chain rendered in R3F. Clicking or scrubbing node blocks lifts them on the Y-axis (`+0.6`), rotates them toward the camera, and illuminates them with an intense emissive `--molten-core` glow (`emissiveIntensity: 1.5`), connected by animated dashed data-flow lines.

---

## 🧪 Evaluation Harness & Metrics

Directory: `evals/`

Executed full evaluation harness (`python evals/harness.py --full`) against **104 held-out synthetic test events**:

```bash
python evals/harness.py --full
```

### Held-Out Dataset Results

| Metric | Measured Value | Benchmark Target | Status |
|---|---|---|---|
| **Total Events Evaluated** | **104** | held_out_set.json | Verified |
| **Total Revenue at Risk** | **₹858,716.15** | Full test dataset | Verified |
| **Total Revenue Recovered** | **₹81,846.20 (9.5%)** | Active recovery cases | [PASS] |
| **Payment Failure Root-Cause Accuracy** | **98.5% (76/77)** | Discoverable banking/mandate failures | [PASS] |
| **Checkout Abandonment Segment** | **27 events** | Isolated behavioral segment | [PASS] |
| **LLM Fallback Accuracy** | **88.9% (8/9 correct)** | Well-calibrated (70.2% avg confidence) | [PASS] |
| **Deterministic Rule Hit Ratio** | **91.3% (95/104)** | > 85.0% | [PASS] |
| **Nuisance-Suppressed Cases** | **13 (12.5%)** | Self-resolution probability > 55% | [PASS] |
| **Compliance Violations** | **0** | Must be 0 | [PASS] |
| **Webhook Signature Verification** | **100% HMAC-SHA256** | 400 Bad Request on invalid | [PASS] |
| **Webhook Idempotency Deduplication** | **100% Replay Protection** | 200 OK duplicate_webhook no-op | [PASS] |
| **p50 Latency (Event → Action)** | **0.0 ms** | < 500 ms | [PASS] |
| **p95 Latency (Event → Action)** | **891.0 ms** | < 1500 ms | [PASS] |

### Baseline Comparison

| Approach | Revenue Recovered (₹) | Recovery Rate (%) | Lift vs. Baseline |
|---|---|---|---|
| **Do Nothing** | ₹0.00 | 0.0% | Baseline |
| **Naive Retry-Everything** | ₹100,997.68 | 11.8% | +₹100,997.68 |
| **Recoup Agent (Full Pipeline)** | **₹81,846.20** | **9.5%** | **Responsible Recovery (13 Suppressed)** |

> **Pitch Framing:** "We recovered ₹81,846.20 while deliberately avoiding unnecessary customer contact on 13.5% of cases identified by our Nuisance-Suppression Scorer as likely self-resolving — responsible recovery, not maximum annoyance."

---

## ⚙ Configuration Reference

All settings loaded from `.env` via `pydantic-settings` (`app/config.py`):

| Variable | Default | Description |
|---|---|---|
| `RAZORPAY_KEY_ID` | `""` | Razorpay test-mode Key ID |
| `RAZORPAY_KEY_SECRET` | `""` | Razorpay test-mode Key Secret |
| `RAZORPAY_WEBHOOK_SECRET` | `""` | Razorpay webhook signature verification secret |
| `GROQ_API_KEY` | `""` | Primary Groq API key |
| `GROQ_MODEL_ID` | `openai/gpt-oss-120b` | Primary Groq model ID |
| `GROQ_WHISPER_MODEL_ID` | `whisper-large-v3-turbo` | Groq Whisper STT model |
| `GEMINI_API_KEY` | `""` | Google Gemini API key (fallback) |
| `GEMINI_MODEL_ID` | `gemini-2.5-flash` | Fallback Gemini model ID |
| `HUMAN_APPROVAL_THRESHOLD_INR` | `5000.0` | ₹ threshold above which human approval is required |
| `MAX_RETRY_ATTEMPTS` | `3` | Max recovery attempts per case |
| `DND_START_HOUR` | `21` | Do-Not-Disturb start hour (IST, 24h) |
| `DND_END_HOUR` | `8` | Do-Not-Disturb end hour (IST, 24h) |
| `DATABASE_URL` | `sqlite:///./recoup.db` | SQLite audit store URL |

---

## 🐳 Deployment

### Production Docker Container

```bash
# Build and run agent service + web dashboard
docker-compose -f infra/docker-compose.yml up --build -d

# View live logs
docker-compose -f infra/docker-compose.yml logs -f

# Stop containers
docker-compose -f infra/docker-compose.yml down
```

---

## 📁 Project Structure

```
recoup/
├── 📄 README.md                          # ← You are here
├── 📄 .env.example                       # Environment template
├── 📂 apps/
│   ├── 📂 agent-service/                 # FastAPI + LangGraph Agent
│   │   ├── 📄 Dockerfile
│   │   ├── 📄 requirements.txt
│   │   ├── 📂 app/
│   │   │   ├── 📄 main.py               # FastAPI application setup
│   │   │   ├── 📄 config.py             # Pydantic Settings
│   │   │   ├── 📂 api/                  # REST endpoints (routes.py)
│   │   │   ├── 📂 graph/                # LangGraph StateGraph (8 nodes)
│   │   │   │   ├── 📄 pipeline.py       # Graph entrypoint
│   │   │   │   ├── 📄 state.py          # Typed RecoveryCase state
│   │   │   │   ├── 📄 detector.py       # Node 1: Ingestion & Risk calculation
│   │   │   │   ├── 📄 diagnoser.py      # Node 2: Hybrid Rules + Groq/Gemini LLM
│   │   │   │   ├── 📄 suppression.py    # Node 3: Nuisance-Suppression Scorer
│   │   │   │   ├── 📄 strategist.py     # Node 4: Policy table + Message drafting
│   │   │   │   ├── 📄 gate.py           # Node 5: Compliance guardrail gate
│   │   │   │   ├── 📄 executor.py       # Node 6: Razorpay API & Voice synthesis
│   │   │   │   ├── 📄 auditor.py        # Node 7: SQLite audit trail & Java ledger dispatch
│   │   │   │   └── 📄 reporter.py       # Node 8: Metrics aggregator
│   │   │   ├── 📂 classifiers/          # Rules engine & LLM classifier
│   │   │   ├── 📂 channels/             # gTTS Hinglish voice channel adapter
│   │   │   ├── 📂 razorpay_client/      # Typed Razorpay API client
│   │   │   └── 📂 webhooks/             # HMAC signature verify & SQLite deduplication
│   │   └── 📂 tests/                    # Proof verification scripts
│   └── 📂 web/                          # React + Vite Neobrutalist Dashboard
│       ├── 📄 Dockerfile
│       ├── 📄 package.json
│       ├── 📄 index.html
│       └── 📂 src/
│           ├── 📂 components/           # MoltenHero3D, TraceLedgerBlocks, ApprovalQueue, etc.
│           ├── 📂 pages/                # Dashboard.tsx, CaseDetail.tsx
│           └── 📂 styles/               # tokens.css (Design tokens)
├── 📂 packages/
│   └── 📂 shared-schemas/               # Shared JSON Schema contracts
├── 📂 data/
│   ├── 📂 generator/                    # Synthetic transaction event generator
│   └── 📂 samples/                      # Tuning (300+) & Held-out (104) datasets
├── 📂 evals/
│   ├── 📄 harness.py                    # Evaluation harness script
│   └── 📂 reports/                      # Generated eval reports (report.md)
├── 📂 infra/
│   ├── 📄 docker-compose.yml
│   └── 📂 .github/workflows/ci.yml      # CI build & test pipeline
└── 📂 docs/                             # ADRs & Architecture docs
```

---

## 📉 Failure Log & Known Limitations

1. **LLM Output Formatting Drift**: Loose text or markdown code fences returned by LLM models are handled via robust regex fallback parsing in `llm_classifier.py`.
2. **WebGL Context Loss on Low-End Devices**: Handled gracefully with fallback CSS gradients and reduced motion options (`prefers-reduced-motion`).
3. **API Rate Limit Guarding**: When Groq returns `429 Too Many Requests`, the provider fallback chain automatically switches execution to Gemini (`gemini-2.5-flash`).

---

## 🗺 Roadmap

- [ ] **Multi-Merchant SaaS Deployment**: Multi-tenant merchant isolation with custom guardrail thresholds.
- [ ] **Real-time Web Speech API Voice Interaction**: Full duplex real-time Hinglish voice conversation.
- [x] **Java Spring Boot Audit Ledger Microservice**: Standalone microservice with SHA-256 hash-chaining and tamper-evident integrity verification.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">
  <br />
  <h2>❤️ Built with Love by</h2>
  <h1><strong>Ankan Basu</strong></h1>
  <p><strong>B.Tech Computer Science & Engineering (CSE) Student at Lovely Professional University (LPU)</strong></p>
  <br />
  <p><em>Vaapsi (वापसी) — "Jo paisa gaya, wapas aayega."</em></p>
  <br />
</div>
