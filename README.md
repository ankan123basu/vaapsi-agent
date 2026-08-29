# 🔄 Vaapsi (वापसी)

> **"Jo paisa gaya, wapas aayega."**
> *Autonomous, Explainable, Compliance-Bounded Revenue Recovery Agent for Indian Merchants*

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-FF6A1A?style=for-the-badge)](https://langchain.com)
[![React 19](https://img.shields.io/badge/React-19.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.2-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![Three.js](https://img.shields.io/badge/Three.js-R3F-black?style=for-the-badge&logo=three.js&logoColor=white)](https://threejs.org)
[![Razorpay](https://img.shields.io/badge/Razorpay-Track_03-0C2340?style=for-the-badge&logo=razorpay&logoColor=white)](https://razorpay.com)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

**Vaapsi (वापसी)** is an autonomous AI agent that detects revenue leaking out of a merchant's payment funnel — failed payments, abandoned checkouts, and failed subscription mandates — diagnoses *why* it leaked, chooses the right recovery intervention, executes it through Razorpay's test-mode APIs, synthesizes Hinglish voice calls, and proves in hard numbers how much money it got back.

**Built for:** Razorpay AI Buildathon — Track 03 (AI Revenue Recovery)

---

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
  - [7-Node LangGraph State Machine](#7-node-langgraph-state-machine)
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

**Recoup** introduces an autonomous, explainable, compliance-bounded AI agent that acts as an expert revenue recovery strategist:
1. **Detects** payment failures in real time via Razorpay webhooks.
2. **Diagnoses** the exact root cause using a hybrid deterministic-rules engine and Groq LLM reasoning.
3. **Selects** the optimal recovery action (Hinglish voice call, smart UPI payment link, retry schedule).
4. **Enforces** strict regulatory guardrails (DND hours, opt-outs, retry caps, ₹5,000 human approval threshold).
5. **Executes** recovery via Razorpay APIs & gTTS voice synthesis with full explainable audit trails.

---

## ⚡ Key Differentiators

| Feature | Recoup Agent | Typical Recovery Tool |
|---|---|---|
| **Root Cause Diagnosis** | Hybrid Rules + Groq `openai/gpt-oss-120b` (87%+ deterministic, fallback to LLM) | Hardcoded strings or static error mapping |
| **Model Diversity & Fallback** | Primary Groq (`openai/gpt-oss-120b`) $\rightarrow$ Automatic Gemini (`gemini-2.5-flash`) fallback | Single model; crashes on provider outages |
| **Voice Recovery Channel** | Live Multi-Language voice call synthesis via `gTTS` (English, Hindi, Hinglish, Tamil, Bengali) with Groq Whisper STT | Plain text SMS or WhatsApp template spam |
| **Compliance-by-Design** | Strict binding guardrails: DND hours (9 PM–8 AM IST), opt-outs, 3 retry cap, ₹5,000 threshold | No compliance checks; risks spam penalties |
| **Explainable Audit Ledger** | Interactive 3D LangGraph decision-trace viewer (`TraceLedgerBlocks.tsx`) | Black-box automated retries |
| **Webhook Idempotency** | HMAC-SHA256 signature verification + SQLite deduplication store | Vulnerable to replay attacks and out-of-order duplicates |
| **Baseline Evaluation** | Held-out 104-event test set evaluated against Do-Nothing and Naive Retry baselines | Unverified vanity numbers |

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

## 🏗 Architecture Overview

### High-Level System Architecture

```
                       ┌───────────────────────────────────────────────────────────┐
                       │  Razorpay Webhook / Synthetic Events Ingestion             │
                       └─────────────────────────────┬─────────────────────────────┘
                                                     │
                                                     ▼
                       ┌───────────────────────────────────────────────────────────┐
                       │  HMAC-SHA256 Signature Verification & SQLite Idempotency   │
                       └─────────────────────────────┬─────────────────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 LangGraph 7-Node StateMachine Core                                      │
│                                                                                                         │
│  [1. Detector] ──► [2. Diagnoser] ──► [3. Strategist] ──► [4. Guardrail Gate] ──► [5. Executor]         │
│                        (Hybrid)            (Policy)             (Boundaries)         (APIs / Voice)     │
│                                                                                           │             │
│                                                                                           ▼             │
│                                                   [7. Reporter] ◄────────────── [6. Auditor]            │
│                                                    (Dashboard)                  (SQLite DB)             │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
                       ┌───────────────────────────────────────────────────────────┐
                       │  React 19 Neobrutalist Dashboard (100vh 3D WebGL Canvas) │
                       └───────────────────────────────────────────────────────────┘
```

---

### 7-Node LangGraph State Machine

The core orchestration engine lives in `apps/agent-service/app/graph/` and is implemented as a pure LangGraph `StateGraph`:

1. **Detector (`detector.py`)**: Parses incoming webhook payload, computes risk exposure, and instantiates typed `RecoveryCase` state.
2. **Diagnoser (`diagnoser.py`)**: Runs deterministic rules engine (`rules_engine.py`) first. If ambiguous, invokes Groq `openai/gpt-oss-120b` (with Gemini fallback) to output root cause JSON.
3. **Strategist (`strategist.py`)**: Consults a deterministic policy table to map root cause $\rightarrow$ channel & recovery action. Uses LLM solely to draft personalized Hinglish copy.
4. **Guardrail Gate (`gate.py`)**: Checks 4 regulatory & business constraints (DND hours, opt-outs, max retries, ₹5,000 threshold). Blocks or flags for human approval if breached.
5. **Executor (`executor.py`)**: Executes action via Razorpay API (creates payment links, schedules mandate retries) or synthesizes Hinglish voice calls (`voice.py`).
6. **Auditor (`auditor.py`)**: Writes immutable node-by-node execution trail into SQLite audit ledger (`recoup.db`).
7. **Reporter (`reporter.py`)**: Aggregates metrics (recovery rate, lift, latency, compliance status) for the REST API.

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
| **Total Revenue at Risk** | **₹745,090.99** | Full test dataset | Verified |
| **Total Revenue Recovered** | **₹100,278.46 (13.5%)** | Maximum recoverable | [PASS] |
| **Lift vs. Naive Retry** | **+₹3,477.38 (+3.6%)** | > 0.0% | [PASS] |
| **Deterministic Rule Hit Ratio** | **93.3% (97/104)** | > 85.0% | [PASS] |
| **Compliance Violations** | **0** | Must be 0 | [PASS] |
| **p50 Latency (Event → Action)** | **0.0 ms** | < 500 ms | [PASS] |
| **p95 Latency (Event → Action)** | **16.0 ms** | < 1500 ms | [PASS] |

### Baseline Comparison

| Approach | Revenue Recovered (₹) | Recovery Rate (%) | Lift vs. Baseline |
|---|---|---|---|
| **Do Nothing** | ₹0.00 | 0.0% | Baseline |
| **Naive Retry-Everything** | ₹96,801.08 | 13.0% | +₹96,801.08 |
| **Recoup Agent (Full Pipeline)** | **₹100,278.46** | **13.5%** | **+₹3,477.38 (+3.6%)** |

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
│   │   │   ├── 📂 graph/                # LangGraph StateGraph (7 nodes)
│   │   │   │   ├── 📄 pipeline.py       # Graph entrypoint
│   │   │   │   ├── 📄 state.py          # Typed RecoveryCase state
│   │   │   │   ├── 📄 detector.py       # Node 1: Ingestion & Risk calculation
│   │   │   │   ├── 📄 diagnoser.py      # Node 2: Hybrid Rules + Groq/Gemini LLM
│   │   │   │   ├── 📄 strategist.py     # Node 3: Policy table + Message drafting
│   │   │   │   ├── 📄 gate.py           # Node 4: Compliance guardrail gate
│   │   │   │   ├── 📄 executor.py       # Node 5: Razorpay API & Voice synthesis
│   │   │   │   ├── 📄 auditor.py        # Node 6: SQLite audit trail
│   │   │   │   └── 📄 reporter.py       # Node 7: Metrics aggregator
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
- [ ] **Java Spring Boot Double-Entry Ledger**: Ledger service microservice for high-throughput institutional settlement.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

*Recoup — Stop revenue leaking out of your payment funnel.*
