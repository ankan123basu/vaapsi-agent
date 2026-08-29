# ADR-0001: Technology Choices

**Status:** Accepted  
**Date:** 2026-08-28  
**Context:** Choosing the technology stack for Recoup — an autonomous revenue recovery agent.

## Decision

### Agent Core: Python 3.11 + FastAPI + LangGraph
- LangGraph provides native stateful multi-node agent graphs in Python
- FastAPI for async REST API consumed by the dashboard
- TypedDict state object for full audit trail inspectability

### LLM Providers: Groq (primary) + Gemini (fallback)
- **Groq** (`llama-3.3-70b-versatile`): Dramatically faster inference — directly improves
  the p50/p95 latency metric reported in evals
- **Gemini** (`gemini-2.0-flash`): Fallback when Groq rate-limits during large eval batches
- Model IDs wrapped in single config constants — one-line swap
- Audit trail logs which provider handled each call

### STT: Groq Whisper (`whisper-large-v3-turbo`)
- For the Hinglish voice recovery channel
- Fast enough for conversational transcription

### Dashboard: React 18 + Vite + TypeScript + Tailwind
- 3D via `@react-three/fiber` + `@react-three/drei` (hero + decision trace only)
- Neobrutalist + molten-metal design system

### Database: SQLite
- Zero infrastructure overhead for hackathon demo
- Sufficient for the audit store + case management
- PostgreSQL reserved for the stretch Java ledger service

### Polyglot Architecture (intentional)
- Python owns the agent logic (LangGraph, LLM SDKs)
- Java Spring Boot for the stretch double-entry ledger
- Mirrors real fintech separation of "the system that decides" from
  "the system that is the source of truth for money moved"

## Consequences
- Python/JS/Java polyglot requires docker-compose for one-command spin-up
- Groq model availability may change — config constants enable fast swap
- SQLite limits concurrent writes but is acceptable for demo scale
