# Architectural Decision Records (ADRs) — AuraNode

This document logs key design, technical, and trade-off decisions made during the development of AuraNode.

---

## ADR-001: Autonomous Schema Discovery via MiniLM Embeddings & Agglomerative Clustering
- **Date**: 2026-08-06
- **Context**: Standard GraphRAG systems require human experts to manually curate a fixed ontology (entity & relation types) before processing text. This is rigid and fails when processing domain-specific or diverse corpora.
- **Decision**: Implement an unsupervised schema discovery pipeline in `ingestion/schema_discovery.py`.
  - Raw triplet extraction generates unconstrained labels (e.g. `acquired`, `bought out`, `purchased`).
  - SentenceTransformer (`all-MiniLM-L6-v2`) embeds all unique raw label strings.
  - Agglomerative clustering with cosine distance groups synonymous labels into canonical schema types (e.g. `ACQUIRED`).
  - Saves `schema.json` and outputs quantitative reduction metrics to `schema_metrics.json`.
- **Trade-offs**: Requires a clustering threshold hyperparameter (default distance threshold = 0.35), but completely eliminates human ontology modeling overhead.

---

## ADR-002: Dual Database Architecture (Neo4j AuraDB + Supabase pgvector) with Local Fallbacks
- **Date**: 2026-08-06
- **Context**: AuraNode requires graph traversal capabilities (for multi-hop reasoning) and dense vector similarity search (for chunk retrieval).
- **Decision**: 
  - **Graph Store**: Neo4j AuraDB Free tier (Cypher query language, native 2-hop traversal).
  - **Vector Store**: Supabase PostgreSQL with `pgvector` extension.
  - **Local Fallbacks**: To ensure 100% offline development, testing, and continuous integration without mandatory API credentials, provide local SQLite / NetworkX fallback drivers in `load_to_neo4j.py` and `embed_and_load_pgvector.py`.
- **Trade-offs**: Dual database architecture increases ingestion complexity slightly, but provides native graph path visualization and vector similarity.

---

## ADR-003: CPU-Only Local Development with Colab GPU Extraction
- **Date**: 2026-08-06
- **Context**: The local development machine is CPU-only (AMD Ryzen 5 5600H, 16GB RAM, no local GPU). Large language model extraction (Llama-3 8B) requires GPU acceleration.
- **Decision**:
  - Offline extraction runs on **Google Colab Free-Tier (T4 GPU)** via `notebooks/colab_triplet_extraction.ipynb`.
  - Local CPU execution handles SentenceTransformer embeddings (`all-MiniLM-L6-v2`), FastAPI server, SQLite/NetworkX/Neo4j drivers, and React dashboard.
- **Trade-offs**: Extraction requires running a Colab notebook once per new corpus, but keeps local system fast, responsive, and completely free.

---

## ADR-004: Groq LPU Inference for Low-Latency Grounded Response Generation
- **Date**: 2026-08-06
- **Context**: The backend needs ultra-fast LLM inference to synthesize context into grounded answers with citations.
- **Decision**: Use Groq API with `llama-3.3-70b-versatile` (with automatic fallback to `llama-3.1-8b-instant`). Provide a strict system prompt prohibiting hallucinations and requiring explicit chunk citations `[chunk_id]`.
- **Trade-offs**: Subject to Groq free-tier rate limits, mitigated by backend rate limiting and token optimization.

---

## ADR-005: CC-BY-SA Wikipedia Data Corpus
- **Date**: 2026-08-06
- **Context**: Open-source repositories must avoid embedding proprietary or copyrighted scraped news text in sample datasets.
- **Decision**: Populate `ingestion/sample_data/raw/` strictly with CC-BY-SA public domain Wikipedia articles focused on major AI industry acquisitions and ecosystem partnerships.
