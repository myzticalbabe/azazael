# AI System Inventory — 2026-11-03
**Required by ISO/IEC 42001 Clause 4, NIST AI RMF MAP function**

---

## 1. AI/ML Components Inventory

| Component | Type | Purpose | Data Flow | Risk Level | Owner | Status |
|-----------|------|---------|-----------|------------|-------|--------|
| **PMB Memory** | Vector DB + BM25 | Persistent memory for agents | User prompts → embedding → recall → response | HIGH | kilo lane | PRODUCTION |
| **Engram** | Semantic memory | Long-term agent memory | Prompts → decisions → lessons → recall | HIGH | kilo lane | PRODUCTION |
| **PAMS** | LocalMemoryStore + MCP | Memory + scheduling | Tool calls → memories → reflections | HIGH | freebuff lane | PRODUCTION |
| **Interpreters** | Go/Rust runners | Code execution sandbox | Code → execution → output | MEDIUM | kilo lane | PRODUCTION |
| **INTERPRETERS Go** | Go runner | Go code execution | Go code → binary → output | MEDIUM | kilo lane | PRODUCTION |
| **INTERPRETERS Rust** | Rust runner | Rust code execution | Rust code → binary → output | MEDIUM | kilo lane | PRODUCTION |
| **LLM Providers** | 12 API providers | Inference routing | Prompt → provider → response | HIGH | kilo lane | PRODUCTION |
| **OpenAI** | Cloud LLM | General inference | Prompt → OpenAI → response | HIGH | kilo lane | PRODUCTION |
| **Anthropic** | Cloud LLM | General inference | Prompt → Anthropic → response | HIGH | kilo lane | PRODUCTION |
| **Groq** | Cloud LLM | Fast inference | Prompt → Groq → response | HIGH | kilo lane | PRODUCTION |
| **Gemini** | Cloud LLM | Large context | Prompt → Gemini → response | HIGH | kilo lane | PRODUCTION |
| **Cerebras** | Cloud LLM | Fast inference | Prompt → Cerebras → response | HIGH | kilo lane | PRODUCTION |
| **Mistral** | Cloud LLM | EU inference | Prompt → Mistral → response | HIGH | kilo lane | PRODUCTION |
| **NVIDIA NIM** | Cloud LLM | NVIDIA models | Prompt → NVIDIA → response | HIGH | kilo lane | PRODUCTION |
| **Cohere** | Cloud LLM | Reranking | Query → Cohere → rerank | MEDIUM | kilo lane | PRODUCTION |
| **Cloudflare** | Cloud LLM | Edge inference | Prompt → Cloudflare → response | MEDIUM | kilo lane | PRODUCTION |
| **SiliconFlow** | Cloud LLM | Chinese models | Prompt → SiliconFlow → response | MEDIUM | kilo lane | PRODUCTION |
| **OVHcloud** | Cloud LLM | EU sovereign | Prompt → OVH → response | MEDIUM | kilo lane | PRODUCTION |
| **Pollinations** | Cloud LLM | Free tier | Prompt → Pollinations → response | LOW | kilo lane | PRODUCTION |
| **Local llama.cpp** | Local LLM | Offline inference | Prompt → llama.cpp → response | HIGH | kilo lane | PRODUCTION |
| **Local llama-server** | Local LLM server | Embedding + chat | Text → embedding/chat → vector/text | HIGH | kilo lane | PRODUCTION |
| **Ollama** | Local LLM | Local model serving | Prompt → Ollama → response | MEDIUM | kilo lane | PRODUCTION |
| **OpenVINO Embedding** | Local embedding | mxbai-embed-large | Text → OpenVINO → vector | HIGH | kilo lane | PRODUCTION |
| **Qwen Embedding** | Local embedding | Qwen3-embedding | Text → Qwen → vector | MEDIUM | kilo lane | PRODUCTION |
| **Transformers** | Local embedding | Python fallback | Text → Transformers → vector | LOW | kilo lane | DEVELOPMENT |
| **Sentence Transformers** | Reranker | Cross-encoder | Query+doc → rerank → score | MEDIUM | kilo lane | PRODUCTION |
| **Graphify** | Code graph | Code analysis | Code → graph → queries | MEDIUM | kilo lane | PRODUCTION |
| **CODEX Video** | Video generation | HTML → MP4 | HTML → PIL → ffmpeg → MP4 | LOW | kilo lane | DEVELOPMENT |
| **CODEX Studio** | Video GUI | Tkinter GUI | GUI → HTML → MP4 | LOW | kilo lane | DEVELOPMENT |
| **Eve Unleashed** | Local AI app | Multi-backend | GUI → LLM → response | MEDIUM | kilo lane | DEVELOPMENT |
| **BARTA Scraper** | Web scraper | Job data | URL → scraper → structured data | LOW | freebuff lane | DEVELOPMENT |
| **BARTA MCP** | MCP server | BARTA tools | MCP call → BARTA → response | LOW | freebuff lane | DEVELOPMENT |

---

## 2. Data Flow Summary

```
User Prompt
    │
    ├─→ kilo lane (PMB/Engram) → Context retrieval
    │
    ├─→ LLM Provider Router → Provider selection → Inference
    │       ├─ Cloud: OpenAI/Anthropic/Groq/Gemini/Mistral/Cerebras/Cohere/Cloudflare/NVIDIA/...
    │       └─ Local: llama.cpp / Ollama / OpenVINO
    │
    ├─→ Interpreters (Go/Rust/Python) → Code execution
    │
    ├─→ PAMS (freebuff) → Memory + scheduling
    │
    ├─→ Interpreters (Go/Rust) → Code execution
    │
    ├─→ Embedding (OpenVINO/Ollama/Transformers) → Vector search
    │
    └─→ Graphify → Code graph analysis
```

---

## 3. Risk Assessment

| Component | Data Sensitivity | Attack Surface | Mitigation Status |
|-----------|------------------|----------------|-------------------|
| PMB/Engram | User prompts, memories, decisions | MCP endpoint, memory corruption | HIGH - MCP auth, staged scanner |
| LLM Providers | User prompts, proprietary data | API keys, prompt injection | PARTIAL - No prompt sanitization |
| Local LLM | User prompts, local data | Model weights, prompt injection | PARTIAL - No output validation |
| Interpreters | User code, system access | Code execution, escape | HIGH - Sandboxed, no network |
| PAMS | Appointments, reminders, health | MCP endpoint | PARTIAL - Basic auth |
| Embeddings | User text, code | Vector DB, model weights | PARTIAL - No output validation |
| Graphify | Codebase, architecture | Code execution | MEDIUM - Read-only mostly |

---

## 4. Compliance Mapping

| Standard | Requirement | Coverage | Gap |
|----------|-------------|----------|-----|
| ISO 42001 Clause 4 | AI system context | PARTIAL | No formal policy |
| ISO 42001 Clause 6 | AI risk assessment | NONE | No formal process |
| ISO 42001 Clause 8 | AI system operation | PARTIAL | No monitoring |
| NIST AI RMF MAP | AI system context | PARTIAL | No inventory (now documented) |
| NIST AI RMF MEASURE | Quantitative metrics | PARTIAL | Gates + supervisor |
| NIST AI RMF MANAGE | Risk prioritization | PARTIAL | Board + supervisor |
| EU AI Act | High-risk AI systems | UNKNOWN | Not assessed |

---

## 5. Recommended Actions (Priority)

1. **Define AI Policy** — Formal policy document per ISO 42001 Clause 5
2. **Risk Assessment Process** — Formal risk assessment per ISO 42001 Clause 6
3. **Prompt Injection Detection** — Input sanitization for all LLM calls
4. **Output Validation** — Response validation for all LLM calls
5. **Model Cards** — Documentation for each AI component
5. **Incident Response** — AI-specific incident response plan
6. **Monitoring** — Continuous monitoring of AI system behavior
6. **Human Oversight** — Human-in-the-loop for high-risk decisions