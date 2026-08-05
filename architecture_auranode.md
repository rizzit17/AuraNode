# Architecture — AuraNode: Self-Optimizing GraphRAG Engine with Auto-Schema Discovery

This document describes the system architecture in detail: components, data flow, schemas, API contracts, and the reasoning behind key design decisions. Intended to live at `docs/architecture.md` in the repo, and to serve as the technical reference during interviews.

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
│   → canonical schema.json                 │
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

**Purpose:** Convert raw unstructured text into typed subject-relation-object triplets, using an LLM smart enough for open-ended extraction but cheap enough to run for free.

- **Why Colab, not local:** the developer's machine is CPU-only (Ryzen 5 5600H, 16GB RAM). Llama-3-8B even 4-bit-quantized needs GPU VRAM headroom that a CPU laptop can't give in reasonable time. Colab's free T4 (16GB VRAM) is sufficient for 4-bit inference.
- **Why this is offline/batch, not part of the live backend:** extraction is a one-time (or per-corpus-update) cost. It should never be in the live request path — that's what makes the live system fast and cheap to run on Groq later.
- **Chunking:** `RecursiveCharacterTextSplitter`, ~500–800 tokens per chunk with overlap, to keep each extraction call within a manageable context window and to keep chunk granularity aligned with what will later be embedded and retrieved.
- **Extraction prompt contract:** the model must output *only* a JSON array of:
  ```json
  {"subject": "...", "relation": "...", "object": "...", "subject_type": "...", "object_type": "..."}
  ```
  Including `subject_type`/`object_type` from the start is what makes Stage 2's auto-schema clustering possible — without raw type labels captured here, there's nothing to cluster later.
- **Failure handling:** malformed JSON triggers one retry with a "repair" prompt (feed the bad output back, ask the model to fix it to valid JSON). Chunks that still fail are logged, not silently dropped — the notebook should report a final parse success rate.

**Outputs:** `triplets.jsonl` (each line tagged with source `chunk_id`), `chunks.jsonl` (chunk_id, text, source_doc).

### 2.2 Auto-Schema Discovery & Ingestion Layer (`ingestion/`)

This is the project's core technical differentiator, so it gets the most detail.

**Problem it solves:** LLM extraction produces messy, inconsistent relation/type labels — "acquired," "bought," "purchased," "took over" all mean the same thing but arrive as different strings. A naive graph built directly from raw labels is fragmented and hard to query (you'd need to know every synonym to traverse it). Manually authoring an ontology up front doesn't scale across arbitrary corpora and defeats the "self-optimizing" framing.

**How `schema_discovery.py` works:**
1. Collect every unique raw string that appeared as a `relation`, `subject_type`, or `object_type` across `triplets.jsonl`.
2. Embed each unique string with `all-MiniLM-L6-v2`.
3. Cluster embeddings with `AgglomerativeClustering` on cosine distance (distance threshold is a tunable parameter — document whatever value is chosen and why, since this is a natural interview question).
4. For each cluster, pick or generate a canonical label (e.g., shortest/most frequent member, upper-snake-cased: `ACQUIRED`).
5. Persist the mapping: raw label → canonical label, and the final canonical vocabulary, to `schema.json`.
6. **Log a before/after count** (e.g., "47 raw relation labels → 12 canonical types") — this is the artifact that makes the "auto-schema discovery" claim verifiable rather than just asserted, and it's what goes in the README/resume.

**`load_to_neo4j.py`:**
- Reads `triplets.jsonl` + `schema.json`.
- Rewrites each triplet's raw relation/type labels to their canonical form.
- Writes nodes and relationships via **`MERGE`, not `CREATE`** — this makes ingestion idempotent, so re-running the pipeline (e.g., after adding new documents) doesn't create duplicate nodes for the same entity.
- Each node/edge is tagged with the `chunk_id`(s) it was derived from, preserving traceability from a graph fact back to its source text — this is what lets the backend later cite sources for graph-derived context, not just vector-derived context.
- Local dev fallback: a NetworkX in-memory graph (or exported `.graphml`) so the ingestion logic can be tested without a live AuraDB connection.

**`embed_and_load_pgvector.py`:**
- Embeds each chunk (same MiniLM model, so query-time and ingest-time embeddings are in the same space).
- Writes to a `chunks` table: `chunk_id`, `text`, `source_doc`, `embedding vector(384)`, `entity_ids text[]` (the entity IDs that chunk contributed triplets for — this is the join key between the vector store and the graph).
- Local dev fallback: SQLite + a brute-force in-memory cosine search, or a lightweight FAISS index, so retrieval logic can be developed without a live Supabase connection.

### 2.3 Hybrid Retrieval Backend (`backend/`)

**Design principle:** vector search alone misses relational facts that aren't co-located in a single chunk (e.g., "who did the company Microsoft acquired later get sued by" — probably spans multiple documents). Graph traversal alone misses generic/narrative context that isn't captured in triplet form. Combining both, and being explicit to the LLM about which is which, is the actual value proposition of GraphRAG over plain RAG.

**Request flow for `POST /api/query`:**
1. **Embed** the incoming question with the same MiniLM model used at ingest time.
2. **`vector_search.py`** — cosine similarity search against `pgvector`, return top-K chunks (K configurable, default 5) plus each chunk's linked `entity_ids`.
3. **`graph_search.py`** — parameterized Cypher query, N-hop traversal (default 2, configurable via query param) starting from the entity IDs surfaced by vector search. Returns the neighborhood's nodes, relationships, and the specific path(s) traversed — the path itself (not just the resulting node set) is preserved because the frontend needs it to highlight *why* those nodes are relevant, not just *that* they are.
4. **`hybrid_merge.py`** — combines chunk text and graph facts into a single structured context block with clear delimiters (e.g., `### TEXT EVIDENCE` vs `### GRAPH FACTS`), and dedupes overlapping information (a fact stated in both a chunk and a graph edge shouldn't be sent twice).
5. **`groq_client.py`** — calls Groq's OpenAI-compatible chat completions endpoint with the merged context and a system prompt that constrains the model to: answer only from the provided context, cite the specific `chunk_id`(s) used for each claim, and explicitly say "not enough information" rather than fabricate when the context doesn't cover the question. This constraint is what the (optional, only-if-measured) hallucination-reduction claim rests on.

**Response contract:**
```json
{
  "answer": "string",
  "citations": ["chunk_id_1", "chunk_id_2"],
  "subgraph": {
    "nodes": [{"id": "...", "label": "...", "type": "..."}],
    "edges": [{"source": "...", "target": "...", "relation": "..."}],
    "traversal_path": ["node_id_1", "node_id_2", "..."]
  }
}
```

**Auxiliary routes:**
- `GET /api/graph/subgraph` — thin wrapper so the frontend can independently re-fetch/re-render a subgraph (e.g., on reconnect) without re-running the full query pipeline.
- `GET /api/health` — liveness/readiness check, also useful for the free-tier hosting platform's health checks.

**Cross-cutting concerns:**
- **Config** (`config.py`): all secrets/URIs (Groq key, Neo4j URI/credentials, Supabase connection string) loaded and validated via `pydantic-settings` from environment variables — never hardcoded, never committed (`.env.example` documents the shape, `.env` is gitignored).
- **Rate limiting / API key gate:** since Groq, Neo4j AuraDB, and Supabase free tiers all have usage caps, the public-deployed demo should sit behind at minimum a simple API-key header or basic rate limiting, so a public link can't silently burn the month's quota.
- **Testing:** unit tests for triplet/schema parsing edge cases and the hybrid-merge dedup logic; at least one integration test hitting `/api/query` with mocked Neo4j/pgvector/Groq clients so tests run fast and don't depend on live free-tier services.

### 2.4 Frontend — Reasoning Dashboard (`frontend/`)

**Design principle:** the differentiator feature isn't the chatbot — it's making the graph reasoning *visible*. The UI should make it obvious to a non-technical viewer (recruiter, interviewer) that the system isn't just doing plain vector RAG.

- **Layout:** split-screen. Left = `ChatPanel.tsx` (question in, grounded answer + inline citation chips out). Right = `GraphView.tsx` (the live subgraph for the current answer).
- **`GraphView.tsx`:** renders `subgraph.nodes`/`subgraph.edges` from the query response using `react-force-graph-2d`. The `traversal_path` is rendered with distinct styling (e.g., thicker/colored edges) from the rest of the returned neighborhood, so it's visually obvious which part of the graph the answer is actually "reasoning" over versus incidental context.
- **`CitationCard.tsx`:** clicking a citation chip in the chat expands the original source chunk text — closes the loop between "the model said X" and "here's the exact text that supports X."
- **States to handle explicitly:** loading (query in flight), empty (first load — should explain what the demo corpus is, since interviewers will poke at it live without reading docs first), and error (backend/Groq/DB failures shouldn't produce a blank screen).
- **Deployment:** frontend on Vercel (static build, calls the backend's public URL via `api/client.ts`); backend on Render or Hugging Face Spaces (Dockerized FastAPI app). CORS must be explicitly configured backend-side for the Vercel origin.

---

## 3. Data Contracts Summary

| Artifact | Producer | Consumer | Format |
|---|---|---|---|
| `triplets.jsonl` | Colab notebook | `schema_discovery.py`, `load_to_neo4j.py` | JSONL, one triplet per line, tagged with `chunk_id` |
| `chunks.jsonl` | Colab notebook | `embed_and_load_pgvector.py` | JSONL: `chunk_id`, `text`, `source_doc` |
| `schema.json` | `schema_discovery.py` | `load_to_neo4j.py` | raw→canonical label map + canonical vocab |
| Neo4j graph | `load_to_neo4j.py` | `graph_search.py` | typed nodes/edges, `chunk_id`-tagged |
| `chunks` table (pgvector) | `embed_and_load_pgvector.py` | `vector_search.py` | `chunk_id`, `text`, `source_doc`, `embedding vector(384)`, `entity_ids text[]` |
| `/api/query` response | FastAPI backend | React frontend | JSON — see §2.3 response contract |

---

## 4. Key Design Decisions & Rationale (see also `docs/decisions.md` for the running ADR log)

1. **Extraction happens offline/batch on Colab, never live.** Keeps the live query path fast and keeps the expensive GPU step out of the cost-sensitive serving loop.
2. **Auto-schema discovery via embedding clustering, not a hardcoded ontology.** Makes the pipeline reusable across arbitrary corpora without manual schema authoring — the actual "self-optimizing" claim in the project name.
3. **`MERGE`-based idempotent graph writes.** Lets the ingestion pipeline be re-run safely as new documents are added, without manual dedup.
4. **Same embedding model (MiniLM) at ingest and query time.** Non-negotiable for vector search correctness — mismatched embedding spaces silently degrade retrieval quality in a way that's hard to debug later.
5. **Graph traversal returns the path, not just the neighborhood.** Needed for the frontend's reasoning-trace visualization to be meaningful rather than just "here's a nearby blob of nodes."
6. **Strict "answer only from context, cite sources, say when unsure" system prompt.** Makes any hallucination-reduction claim potentially verifiable via a real eval, rather than an unfounded assertion.
7. **Local-dev fallbacks (NetworkX, SQLite, mock extraction) for every cloud dependency.** Lets development and testing proceed without live free-tier credentials, and keeps free-tier usage reserved for the actual deployed demo.
8. **API-key gate on the public deployment.** Protects free-tier quotas (Groq/Neo4j/Supabase) from being exhausted by public traffic.

---

## 5. Known Open Items (see `context.md` §6 for the up-to-date list)

- Project name is finalized as **AuraNode** across code, docs, and resume material.
- Auto-schema clustering needs a logged before/after count to back the claim with a real number.
- Hallucination-reduction claim needs a real held-out eval before being used on the resume.
- Groq model IDs should be reconfirmed against the current free-tier list at build time.
