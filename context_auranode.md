# Project Context: AuraNode — Self-Optimizing GraphRAG Engine with Auto-Schema Discovery

> Paste this file into any new AI chat (Claude, ChatGPT, Antigravity, etc.) at the start of a session to give it full context on this project without re-explaining from scratch.

---

## 1. What This Project Is

**AuraNode** is a portfolio-grade, end-to-end **GraphRAG (Graph-Augmented Retrieval-Augmented Generation) system** built to demonstrate production-level AI/ML systems engineering for AI Engineer job applications.

**Core idea:** unstructured text → LLM-extracted knowledge graph with **auto-schema discovery** (no hardcoded ontology — entity/relation types are discovered and canonicalized via embedding clustering) → hybrid retrieval (vector search + N-hop graph traversal) → grounded, citation-backed LLM answers → a React dashboard that visualizes the exact subgraph the system "reasoned" over to answer.

The differentiator vs. a generic RAG project: the **auto-schema discovery** step and the **live subgraph reasoning-trace visualization**, not just "chatbot over documents."

---

## 2. Architecture

```
[Unstructured Text Corpus — Wikipedia/public-domain, "AI Ecosystem & Tech Acquisitions" domain]
        │
        ▼
[1. Colab Triplet Extraction — notebooks/colab_triplet_extraction.ipynb]
  - Runs on Google Colab free-tier T4 GPU (developer has no local GPU)
  - LangChain RecursiveCharacterTextSplitter for chunking
  - Quantized Llama-3-8B-Instruct extracts {subject, relation, object, subject_type, object_type} triplets
  - JSON validation + retry-on-malformed-output logic
  - Outputs: triplets.jsonl, chunks.jsonl
        │
        ▼
[2. Auto-Schema Discovery & Ingestion — ingestion/]
  - schema_discovery.py: embeds raw relation/entity-type labels with MiniLM (all-MiniLM-L6-v2),
    clusters via AgglomerativeClustering on cosine distance, merges near-duplicates
    (e.g. "bought"/"purchased"/"acquired" -> canonical "ACQUIRED"), saves schema.json
  - load_to_neo4j.py: idempotent MERGE Cypher writes to Neo4j AuraDB (free tier)
  - embed_and_load_pgvector.py: MiniLM chunk embeddings -> Supabase Postgres + pgvector
  - mock_extraction.py: offline fallback to generate sample triplets/chunks locally without cloud
        │
        ▼
[3. FastAPI Hybrid Retrieval Backend — backend/]
  - vector_search.py: embed query, top-K similarity search in pgvector, return chunks + entity links
  - graph_search.py: Cypher 2-hop neighborhood traversal in Neo4j around matched entities
  - hybrid_merge.py: fuses chunk text + graph facts into one structured context (clear delimiters)
  - groq_client.py: calls Groq API (Llama 3.1/3.3) with strict "answer only from context, cite
    chunk IDs, say 'not enough info' if uncovered" instructions
  - Routes: /api/query, /api/graph/subgraph, /api/health
        │
        ▼
[4. React + TypeScript Reasoning Dashboard — frontend/]
  - ChatPanel.tsx: chat interface, grounded answers, clickable citation chips
  - GraphView.tsx: react-force-graph-2d rendering the live traversed subgraph, with the actual
    reasoning path highlighted distinctly from the rest of the neighborhood
  - CitationCard.tsx: expanded source-chunk view for a clicked citation
  - Deployed: frontend on Vercel, backend on Render or Hugging Face Spaces
```

---

## 3. Tech Stack (zero-cost constraint is deliberate — see §5)

| Layer | Tech |
|---|---|
| Extraction LLM | Llama-3-8B-Instruct (quantized, Colab T4) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, CPU) |
| Graph DB | Neo4j AuraDB (free tier) |
| Vector store | Supabase Postgres + pgvector (free tier) |
| Serving LLM | Groq API — `llama-3.3-70b-versatile` / `llama-3.1-8b-instant` (verify current free-tier model IDs at build time) |
| Backend | FastAPI, pydantic-settings, neo4j-driver |
| Frontend | React + TypeScript + Vite, react-force-graph-2d |
| Hosting | Vercel (frontend), Render or HF Spaces (backend) |
| Local dev fallback | NetworkX / SQLite / in-memory vector store, `mock_extraction.py` — full pipeline runnable offline without cloud keys |

---

## 4. Repository Structure

```
AuraNode/
├── README.md
├── .env.example
├── docs/
│   ├── architecture.md
│   └── decisions.md          # ADR-style log of trade-offs made during build
├── notebooks/
│   └── colab_triplet_extraction.ipynb
├── ingestion/
│   ├── schema_discovery.py
│   ├── load_to_neo4j.py
│   ├── embed_and_load_pgvector.py
│   ├── mock_extraction.py
│   └── sample_data/
│       ├── raw/
│       ├── triplets.jsonl
│       ├── chunks.jsonl
│       └── schema.json
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── routers/ (query.py, graph.py, health.py)
│   │   └── services/ (vector_search.py, graph_search.py, hybrid_merge.py, groq_client.py)
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx
        ├── api/client.ts
        └── components/ (ChatPanel.tsx, GraphView.tsx, CitationCard.tsx)
```

---

## 5. Constraints That Shape Every Decision

- **No local GPU** — developer's machine is CPU-only (Ryzen 5 5600H, 16GB RAM). Anything GPU-heavy (LLM extraction) must run on Colab free-tier T4; everything else must run comfortably on CPU.
- **Zero-cost stack only** — every service must have a genuine free tier (Groq, Neo4j AuraDB, Supabase, Vercel, Render/HF Spaces). No paid services without flagging an alternative first.
- **Local-dev fallback required** — full pipeline should be testable offline (mocks/NetworkX/SQLite) without mandatory cloud keys during development.
- **Build in vertical slices** — get one document → triplets → graph → hybrid search → answer working end-to-end on a tiny sample before scaling or polishing UI.
- **Every phase should leave the repo runnable**, with an accurate README doubling as interview documentation.
- **Resume claims must be true, not aspirational** — e.g., only claim a hallucination-reduction percentage if a real before/after eval (graph-augmented vs. vector-only baseline on held-out questions) is actually run and logged.

---

## 6. Current Status / Open Items

- Naming: project name is finalized as **AuraNode** across code, docs, commits, README, and resume material.
- Demo corpus: recommended domain is "AI Ecosystem & Tech Industry Acquisitions" (Microsoft/OpenAI, Google/DeepMind/Anthropic, Meta/Scale AI, Nvidia/Mellanox/ARM, etc.) — must use Wikipedia/public-domain text only in `sample_data/raw/`, not scraped news, for redistribution reasons.
- Not yet added to the plan: a concrete before/after metric for the auto-schema clustering (e.g., "N raw relation labels → M canonical types," logged/printed by `schema_discovery.py`) so the README/resume has a real number instead of a vibe check.
- Not yet added to the plan: an `eval/` script for the hallucination-reduction claim (small held-out question set, graph-augmented vs. vector-only baseline) — needed if that resume bullet is going to be kept.
- Groq model IDs (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`) should be re-verified against Groq's current free-tier model list at actual build time, since these change.

---

## 7. Resume Framing (only finalize once actually built and verified)

```
Graph-Augmented RAG Engine with Autonomous Schema Discovery | Python, FastAPI, Neo4j, Groq, React, pgvector

- Architected a GraphRAG pipeline with automatic entity/relation schema discovery (embedding-based
  clustering of extracted labels), removing the need for a hand-authored ontology.
- Built a Colab-hosted Llama-3 extraction pipeline turning unstructured text into a typed knowledge
  graph, persisted in Neo4j AuraDB with idempotent, chunk-traceable ingestion.
- Engineered a hybrid retrieval backend (FastAPI) combining pgvector semantic search with 2-hop Neo4j
  graph traversal, serving grounded, citation-backed answers via Groq LPU inference.
- Shipped a React dashboard visualizing the live reasoning trace — the exact subgraph the system
  traversed to answer — alongside the chat interface; deployed end-to-end on Vercel + Render.
```

Do not include a hallucination-reduction % unless it's been measured (see §6).

---

## 8. About the Developer (for context when asking for help on this project)

- Rishit — final-year B.Tech CSE (IoT) student, VIT Vellore (Batch 2027), based in Noida, India.
- Full-stack + ML/LLM background: React, Next.js, MERN, and applied ML/LLM projects.
- Approaching campus placements; this project is being built specifically as a standout portfolio piece for AI Engineer role applications, alongside an existing agentic project ("Cartographer," a LangGraph-based codebase-understanding/refactor engine).
- Runs local dev on a CPU-only machine (Ryzen 5 5600H / 16GB RAM) — no local GPU.
- Prefers resume/portfolio content to use real, defensible metrics rather than unverified or cost-savings-style figures.
