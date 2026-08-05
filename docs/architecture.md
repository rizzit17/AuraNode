# Architecture — AuraNode: Self-Optimizing GraphRAG Engine with Auto-Schema Discovery

This document describes the system architecture in detail: components, data flow, schemas, API contracts, and the reasoning behind key design decisions.

---

## 1. High-Level System Diagram

```
┌──────────────────────────┐
│  Unstructured Text Corpus│  (Wikipedia / public-domain — "AI Ecosystem & Tech Acquisitions")
└─────────────┬─────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ STAGE 1 — Extraction (Google Colab, T4)   │
│  notebooks/colab_triplet_extraction.ipynb │
│                                            │
│  RecursiveCharacterTextSplitter           │
│         │                                 │
│         ▼                                 │
│  Llama-3-8B-Instruct (4-bit quantized)    │
│  Prompt: extract typed triplets → JSON    │
│         │                                 │
│         ▼                                 │
│  JSON validate + retry-on-malformed       │
└─────────────┬──────────────────────────────┘
              │  triplets.jsonl, chunks.jsonl
              ▼
┌──────────────────────────────────────────┐
│ STAGE 2 — Schema Discovery & Ingestion    │
│  ingestion/                               │
│                                            │
│  schema_discovery.py                      │
│   MiniLM embed raw labels → cluster       │
│   (AgglomerativeClustering, cosine dist)  │
│   → canonical schema.json + metrics       │
│         │                                 │
│         ├──► load_to_neo4j.py             │
│         │     idempotent MERGE Cypher     │
│         │     → Neo4j AuraDB              │
│         │                                 │
│         └──► embed_and_load_pgvector.py   │
│               MiniLM chunk embeddings     │
│               → Supabase Postgres/pgvector│
└─────────────┬──────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────┐
│ STAGE 3 — Hybrid Retrieval Backend        │
│  backend/app/ (FastAPI)                   │
│                                            │
│  POST /api/query                          │
│   1. embed question (MiniLM)              │
│   2. vector_search.py → top-K chunks      │
│      + linked entity IDs (pgvector)       │
│   3. graph_search.py → 2-hop neighborhood │
│      around those entities (Neo4j Cypher) │
│   4. hybrid_merge.py → structured context │
│      (text evidence | graph facts)        │
│   5. groq_client.py → Groq API call       │
│      → grounded answer + chunk citations  │
│                                            │
│  GET /api/graph/subgraph                  │
│   returns traversed subgraph as JSON      │
│                                            │
│  GET /api/health                          │
└─────────────┬──────────────────────────────┘
              │  JSON: { answer, citations, subgraph }
              ▼
┌──────────────────────────────────────────┐
│ STAGE 4 — React Reasoning Dashboard       │
│  frontend/src/ (Vite + React + TS)        │
│                                            │
│  ChatPanel.tsx      ◄── chat I/O          │
│  CitationCard.tsx   ◄── source chunk view │
│  GraphView.tsx       ── react-force-graph │
│                        renders subgraph,  │
│                        highlights the     │
│                        actual reasoning   │
│                        path               │
│                                            │
│  Deployed: Vercel (frontend)              │
│            Render / HF Spaces (backend)   │
└────────────────────────────────────────────┘
```

---

## 2. Component Breakdown

### 2.1 Extraction Layer (Colab, offline/batch)
- **Chunking**: `RecursiveCharacterTextSplitter`, ~500–800 tokens/chunk with overlap.
- **Model**: `Llama-3-8B-Instruct` quantized on Colab free T4 GPU.
- **Outputs**: `triplets.jsonl` and `chunks.jsonl`.

### 2.2 Auto-Schema Discovery (`ingestion/schema_discovery.py`)
- Embeds raw triplet labels using `all-MiniLM-L6-v2`.
- Agglomerative clustering on cosine distance.
- Outputs `schema.json` and quantitative stats report `schema_metrics.json` (**44.44% compression**).

### 2.3 Hybrid Retrieval Backend (`backend/app/`)
- Vector similarity search (`pgvector` / MiniLM).
- 2-hop graph neighborhood traversal (Neo4j AuraDB / Cypher).
- Structured context merging (`hybrid_merge.py`).
- Groq LLM grounded synthesis (`groq_client.py`).
- Benchmark evaluation suite (`backend/eval/benchmark_eval.py`).

### 2.4 Frontend Reasoning Dashboard (`frontend/src/`)
- Technical Schematic Neobrutalism UI design.
- Interactive Force-Directed Graph Reasoning trace.
- Clickable citation cards linking answers to exact text evidence.
