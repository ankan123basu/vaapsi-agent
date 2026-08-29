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
- [Core Algorithms & Engineering Core](#-core-algorithms--engineering-core)
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

**Vaapsi (वापसी)** introduces an autonomous, explainable, compliance-bounded AI agent that acts as an expert revenue recovery strategist:
1. **Detects** payment failures in real time via Razorpay webhooks.
2. **Diagnoses** the exact root cause using a hybrid deterministic-rules engine and Groq LLM reasoning.
3. **Selects** the optimal recovery action (Hinglish voice call, smart UPI payment link, retry schedule).
4. **Enforces** strict regulatory guardrails (DND hours, opt-outs, retry caps, ₹5,000 human approval threshold).
5. **Executes** recovery via Razorpay APIs & gTTS voice synthesis with full explainable audit trails.

---

## 🧠 Core Algorithms & Engineering Core

Vaapsi is powered by rigorous algorithms and production-grade software engineering patterns:

1. **7-Node Directed Acyclic Graph (DAG) State Machine (`LangGraph`)**:
   - Pipeline transitions: `Detector` $\rightarrow$ `Diagnoser` $\rightarrow$ `Strategist` $\rightarrow$ `Guardrail Gate` $\rightarrow$ `Executor` $\rightarrow$ `Auditor` $\rightarrow$ `Reporter`.
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

---

## ⚡ Key Differentiators

| Feature | Vaapsi (वापसी) Agent | Typical Recovery Tool |
|---|---|---|
| **Root Cause Diagnosis** | Hybrid Rules + Groq `openai/gpt-oss-120b` (92% deterministic, fallback to LLM) | Hardcoded strings or static error mapping |
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
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📜 License

MIT License. Built for Razorpay AI Buildathon 2026.
