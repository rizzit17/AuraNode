# Master Build Prompt — Self-Optimizing GraphRAG Engine with Auto-Schema Discovery

> Paste everything below into Antigravity (Claude Sonnet) as the project brief. It is written to be self-contained: goals, architecture, exact file structure, phase-by-phase tasks, acceptance criteria, and constraints. Treat each phase as a checkpoint — don't move to the next phase until the current one's acceptance criteria pass.

---

## 0. Role & Operating Instructions for the Agent

You are acting as a senior full-stack + ML systems engineer. Build a production-grade, end-to-end **GraphRAG (Graph-Augmented Retrieval-Augmented Generation) system** called **"AuraNode"**.

Ground rules for how you work on this repo:
1. **Runtime constraints are real, not hypothetical.** The developer has a CPU-only machine (Ryzen 5 5600H, 16GB RAM, no local GPU). Any step requiring a GPU (LLM-based triplet extraction) must run on **Google Colab free-tier T4**, not locally. Everything else (embeddings, FastAPI backend, React frontend, DB writes) must run comfortably on a CPU laptop.
2. **Zero-cost stack only.** Every service used must have a genuinely free tier: Groq API (inference), Neo4j AuraDB Free, Supabase Postgres free tier (with pgvector), Vercel (frontend hosting), Render or Hugging Face Spaces (backend hosting), Hugging Face `sentence-transformers/all-MiniLM-L6-v2` (local embeddings). Do not introduce paid services without flagging it explicitly and offering a free alternative first.
3. **Build in vertical slices, not horizontal layers.** Get one document → triplets → graph → hybrid search → answer working end-to-end on a tiny sample *first*, before scaling up or polishing UI. A working ugly pipeline beats a beautiful broken one.
4. **Every phase must leave the repo in a runnable state.** Commit after each working milestone. Include a `README.md` that stays accurate as you go — this doubles as resume/interview documentation.
5. **Explain trade-offs as you go**, especially anywhere you deviate from the plan below (e.g., swapping Neo4j for an in-memory graph if AuraDB free tier proves too restrictive). Surface these decisions instead of silently改.
6. **Write tests for the non-trivial logic**: triplet parsing/validation, hybrid retrieval merge logic, the graph-hop traversal, and the API routes. Doesn't need to be exhaustive — just enough that a recruiter or interviewer skimming the repo sees engineering discipline.

---

## 1. Project Goal (what "done" looks like)

A live, deployed system where:
- A user uploads or points to an unstructured text corpus (e.g., a set of company reports, Wikipedia articles, or news dumps).
- An offline pipeline (run once per corpus, in Colab) extracts an entity-relationship knowledge graph from the text using an LLM, with **auto-schema discovery** — i.e., the system does not use a hardcoded ontology of entity/relation types; it discovers and normalizes types as it processes the corpus.
- That graph is persisted in Neo4j AuraDB, and the source chunks are embedded and stored in pgvector.
- A FastAPI backend exposes a `/api/query` endpoint that does **hybrid retrieval**: vector similarity search over chunks + N-hop graph traversal around the matched entities, merges both into a single context, and calls Groq (Llama 3.1/3.3) to generate a grounded answer with citations back to source chunks.
- A React dashboard lets a user ask questions in a chat panel and, side-by-side, **visualizes the actual subgraph the system traversed to answer** — this visual "reasoning trace" is the centerpiece resume/demo feature.
- The whole thing is deployed and publicly clickable (Vercel + Render/HF Spaces), with a demo video/GIF in the README.

---

## 2. System Architecture

```
[Raw corpus: .txt/.pdf/.md files]
        │
        ▼
[Google Colab, T4 GPU]
  - LangChain text splitter → chunks
  - Llama-3-8B-Instruct (via Colab-hosted inference or Groq) → JSON triplets per chunk
  - Auto-schema normalizer: clusters raw relation/entity type strings into a canonical schema
  - Output: triplets.jsonl + chunks.jsonl
        │
        ▼ (manual or scripted export)
[Local ingestion script — Python, run from repo]
  - Reads triplets.jsonl + chunks.jsonl
  - Writes nodes/edges to Neo4j AuraDB (Cypher, via neo4j-driver)
  - Embeds chunks with all-MiniLM-L6-v2 (local CPU, sentence-transformers)
  - Writes chunk text + embeddings to Postgres/pgvector (Supabase)
        │
        ▼
[FastAPI backend]
  - /api/query route
    1. Embed the user question (same MiniLM model)
    2. Vector search in pgvector → top-k relevant chunks + their linked entity IDs
    3. Graph traversal in Neo4j (2-hop, configurable) around those entity IDs
    4. Merge: text chunks + graph neighborhood → structured context block
    5. Call Groq API (Llama 3.1/3.3-70B or similar) with context → grounded answer + citations
  - /api/graph/subgraph route → returns the exact traversed subgraph as JSON for visualization
  - /api/corpus/status, /api/health, etc.
        │
        ▼
[React + TypeScript frontend]
  - Left panel: chat interface (question in, grounded answer + source citations out)
  - Right panel: force-directed graph visualization (react-force-graph or vis-network) rendering
    the exact subgraph returned by /api/graph/subgraph, highlighting the traversal path
  - Deployed on Vercel; backend deployed on Render or HF Spaces
```

---

## 3. Repository Structure

```
graphrag-engine/
├── README.md
├── docs/
│   ├── architecture.md
│   ├── demo.gif
│   └── decisions.md            # ADR-style log of trade-offs made during build
├── notebooks/
│   └── colab_triplet_extraction.ipynb   # Phase 1 — runs on Colab T4
├── ingestion/
│   ├── schema_discovery.py     # clusters/normalizes raw relation & entity type strings
│   ├── load_to_neo4j.py
│   ├── embed_and_load_pgvector.py
│   └── sample_data/            # small demo corpus, committed to repo
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── query.py
│   │   │   ├── graph.py
│   │   │   └── health.py
│   │   ├── services/
│   │   │   ├── vector_search.py
│   │   │   ├── graph_search.py
│   │   │   ├── hybrid_merge.py
│   │   │   └── groq_client.py
│   │   ├── models/              # pydantic schemas
│   │   └── config.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatPanel.tsx
│   │   │   ├── GraphView.tsx
│   │   │   └── CitationCard.tsx
│   │   ├── api/client.ts
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
└── .env.example
```

---

## 4. Phase-by-Phase Build Plan

### Phase 1 — Knowledge Graph Extraction (Colab, Days 1–4)
**Deliverable:** `notebooks/colab_triplet_extraction.ipynb`, runnable top-to-bottom on Colab free T4, producing `triplets.jsonl` and `chunks.jsonl` in `ingestion/sample_data/`.

Tasks:
1. Load a small sample corpus (~10–20 documents; use public-domain text — Wikipedia extracts on a chosen domain like "big tech acquisitions" work well for a demo) into `ingestion/sample_data/raw/`.
2. Use LangChain's `RecursiveCharacterTextSplitter` to chunk documents (target ~500–800 tokens/chunk, with overlap).
3. Load `meta-llama/Meta-Llama-3-8B-Instruct` (or an equivalent open model available on Colab free tier) via `transformers` + `bitsandbytes` 4-bit quantization so it fits the T4's 16GB VRAM.
4. Extraction prompt: strict instruction to output **only** a JSON array of `{subject, relation, object, subject_type, object_type}` — include type fields from the start, since that's what auto-schema discovery clusters over.
5. Run extraction per chunk, with retry-on-malformed-JSON logic (parse failures should not silently drop data — log and retry once with a repair prompt).
6. Write `triplets.jsonl` (one JSON object per line, each tagged with its source `chunk_id`) and `chunks.jsonl` (chunk_id, text, source_doc).

**Acceptance criteria:** Running the notebook on a fresh Colab T4 instance produces valid `triplets.jsonl`/`chunks.jsonl` for the full sample corpus with a documented (in the notebook) success/failure parse rate.

### Phase 2 — Auto-Schema Discovery + Database Setup (Days 5–7)
**Deliverable:** `ingestion/schema_discovery.py`, `ingestion/load_to_neo4j.py`, `ingestion/embed_and_load_pgvector.py`, populated free-tier Neo4j AuraDB + Supabase pgvector instances.

Tasks:
1. **This is the "auto-schema discovery" that makes the project stand out — don't skip or fake it.** Implement `schema_discovery.py`:
   - Collect all raw `relation` strings and `subject_type`/`object_type` strings from `triplets.jsonl`.
   - Embed each unique string with MiniLM, cluster with a simple algorithm (e.g., agglomerative clustering or DBSCAN on cosine distance) to merge near-duplicate labels (e.g., "acquired", "bought", "purchased" → canonical `ACQUIRED`).
   - Persist the discovered canonical schema (`schema.json`: mapping raw label → canonical label, plus the final entity-type and relation-type vocabularies) — this artifact is itself worth showing in the demo/README as evidence the schema wasn't hardcoded.
2. Set up a free Neo4j AuraDB instance; store connection creds in `.env` (never commit secrets — commit `.env.example` only).
3. `load_to_neo4j.py`: reads triplets + canonical schema, writes `MERGE` (not `CREATE`, to keep it idempotent) Cypher for nodes and typed relationships, tagging each edge/node with its source `chunk_id`(s) for traceability.
4. Set up Supabase Postgres with the `pgvector` extension enabled; create a `chunks` table (`chunk_id`, `text`, `source_doc`, `embedding vector(384)`, `entity_ids text[]`).
5. `embed_and_load_pgvector.py`: embeds each chunk with MiniLM (CPU, local), links each chunk to the entity IDs it produced triplets for, writes rows to Supabase.

**Acceptance criteria:** Neo4j Browser shows a connected, typed graph for the sample corpus; a SQL query against Supabase returns nearest-neighbor chunks for a test embedding; `schema.json` shows meaningfully fewer canonical types than raw extracted labels (evidence the clustering did something).

### Phase 3 — Hybrid Retrieval Backend (Days 8–11)
**Deliverable:** working FastAPI backend, `backend/`, with `/api/query` and `/api/graph/subgraph` fully functional against the real databases.

Tasks:
1. Scaffold FastAPI app with routers as per the repo structure above. Use Pydantic models for request/response schemas.
2. `services/vector_search.py`: embed incoming question, cosine-similarity search in pgvector (top-k configurable, default 5), return matched chunks + their linked entity IDs.
3. `services/graph_search.py`: given entity IDs, run a parameterized Cypher query for N-hop neighborhood (default 2 hops, configurable via query param), return nodes + relationships + the specific path taken.
4. `services/hybrid_merge.py`: combine chunk text + graph neighborhood into one structured context block (clear delimiters — text evidence vs. graph facts — so the LLM can distinguish and the frontend can cite each separately).
5. `services/groq_client.py`: call Groq's OpenAI-compatible endpoint with the merged context + question; system prompt should instruct the model to answer **only from provided context**, cite chunk IDs it used, and say "not enough information" if the graph+chunks don't cover it (this matters for the hallucination-reduction claim on the resume — make it actually true, don't just claim it).
6. `/api/query` returns: `{answer, citations: [chunk_id...], subgraph: {nodes, edges, traversal_path}}`.
7. `/api/graph/subgraph` is a thin wrapper so the frontend can re-fetch/re-render the graph independently if needed.
8. Add basic auth/rate-limiting guard (even a simple API-key header) since Groq/Neo4j/Supabase free tiers have usage caps you don't want burned by a public demo.
9. Write tests: triplet/schema parsing edge cases, hybrid merge logic (does it correctly dedupe overlapping chunk/graph info?), and at least one integration test hitting a route with a mocked LLM call.

**Acceptance criteria:** `curl` or Postman against `/api/query?q=...` on the sample corpus returns a grounded, cited answer within a few seconds; malformed/empty queries are handled gracefully (no 500s).

### Phase 4 — Frontend & Observability Dashboard (Days 12–14)
**Deliverable:** deployed React app on Vercel, backend deployed on Render/HF Spaces, demo GIF in README.

Tasks:
1. Scaffold with Vite + React + TypeScript. Split-screen layout: chat on the left, graph canvas on the right.
2. `ChatPanel.tsx`: input box, message history, renders the LLM answer with inline citation chips that scroll/highlight the corresponding source in a `CitationCard.tsx` panel.
3. `GraphView.tsx`: use `react-force-graph-2d` (lighter weight, good default) to render the subgraph JSON from `/api/graph/subgraph` — style traversed-path edges distinctly from the rest of the neighborhood so the "reasoning trace" is visually obvious. This is the single highest-leverage feature for a live demo/interview — invest real polish here.
4. Loading states, error states, and an empty state that explains what the demo corpus is (since interviewers will poke at it live).
5. Deploy backend to Render (Docker) or HF Spaces; deploy frontend to Vercel; wire up CORS + environment variables correctly.
6. Record a 30–60s screen-capture GIF of a real query flowing through the UI; drop it in `docs/demo.gif` and embed at the top of `README.md`.
7. Write the final `README.md`: problem statement, architecture diagram (ASCII or exported image), setup instructions, live demo link, and the auto-schema-discovery explanation (this is the differentiator — make sure it's legible to a non-expert reader).

**Acceptance criteria:** A stranger can open the deployed Vercel link, ask a question about the demo corpus, see a cited answer and a rendered subgraph, with no setup on their end.

---

## 5. Resume Framing (for reference — keep consistent with what you actually build)

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

Only keep the "reduced hallucination by X%" style claim if you actually run a small before/after eval (e.g., 20 held-out questions, graph-augmented vs. vector-only baseline, manual or LLM-judged grounding score) and get a real number — don't carry over the unverified "35%" figure from the original idea doc.

---

## 6. Open Decisions to Resolve Before Coding

Ask/decide these before Phase 1, and record the answer in `docs/decisions.md`:
1. Domain/corpus for the demo (tech acquisitions, a specific industry, historical events, etc.) — pick something visually interesting when graphed and safe to publish.
2. Neo4j AuraDB vs. staying inside Postgres with a graph-shaped schema (recursive CTEs) — the original idea flagged this trade-off; Neo4j is recommended for a stronger visualization story and cleaner Cypher-based traversal, but note the trade-off explicitly in the docs.
3. Exact Groq model to standardize on (check current Groq free-tier model list at build time, since availability changes).
4. Whether auth is needed on the public demo to protect free-tier quotas (recommended: yes, simple API key or rate limit).

---

## 7. What "complete" means

Ship when all four phase acceptance criteria pass, the app is live at a public URL, the README is interview-ready, and the resume bullets above are true statements about what was actually built — not aspirational ones.
