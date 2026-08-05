# AuraNode — Self-Optimizing GraphRAG Engine with Autonomous Schema Discovery

> **AuraNode** is a production-grade Graph-Augmented Retrieval-Augmented Generation (GraphRAG) engine that autonomously discovers entity/relation schemas from unstructured text, fuses vector similarity search with N-hop graph traversal, and visualizes interactive reasoning subgraphs in real time.

---

## 🌟 Key Features

- **Autonomous Schema Discovery**: No hand-authored ontology required. Automatically extracts raw entity-relation triplets and uses embedding-based clustering (`all-MiniLM-L6-v2` + Agglomerative Clustering) to synthesize canonical entity and relationship schemas.
- **Hybrid Retrieval Architecture**: Combines `pgvector` semantic similarity search over text chunks with 2-hop Neo4j Cypher graph neighborhood traversal.
- **Interactive Reasoning Subgraph Visualizer**: Real-time 2D force-directed graph canvas (`react-force-graph-2d`) that highlights the exact graph traversal path taken to answer a query.
- **Grounded & Citation-Backed LLM Generation**: Instructs Groq Llama 3.3 / 3.1 models to generate answers strictly from retrieved context with explicit chunk citations `[chunk_id]`.
- **Zero-Cost Stack**: Built to run entirely on free-tier infrastructure (Google Colab GPU, Neo4j AuraDB Free, Supabase pgvector, Groq LPU, Vercel, Render/HF Spaces).
- **Comprehensive Evaluation Suite**: Includes quantitative benchmarking (`backend/eval/benchmark_eval.py`) comparing Vector-Only vs. Graph-Augmented RAG grounding and hit-rate accuracy.

---

## 🏗️ System Architecture

```
[Raw Corpus (CC-BY-SA Wikipedia Data)]
        │
        ▼
[Google Colab (T4 GPU Extraction)]
  - LangChain Text Splitter
  - Quantized Llama 3 8B Instruct -> Raw triplets.jsonl + chunks.jsonl
        │
        ▼
[AuraNode Ingestion Pipeline]
  - schema_discovery.py -> MiniLM Clustering -> Canonical schema.json + schema_metrics.json
  - load_to_neo4j.py -> Idempotent Cypher writes (Neo4j AuraDB)
  - embed_and_load_pgvector.py -> SentenceTransformer -> Supabase pgvector
        │
        ▼
[FastAPI Hybrid Retrieval Backend]
  - /api/query: pgvector search + Neo4j 2-hop Cypher traversal + Context Fusion + Groq LLM
  - /api/graph/subgraph: Reasoning subgraph graph payload
        │
        ▼
[React + TypeScript Reasoning Dashboard]
  - Left Panel: Chat interface with grounded answer & citation chips
  - Right Panel: Interactive Force-Directed Subgraph rendering reasoning trace
```

---

## 📊 Quantitative Benchmark & Schema Metrics

- **Auto-Schema Discovery Efficiency**: Logged in `ingestion/sample_data/schema_metrics.json`.
- **Retrieval Grounding & Accuracy**: Benchmark script in `backend/eval/benchmark_eval.py` outputs comparative results in `docs/evaluation_report.json`.

---

## 🛠️ Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API Key (Free)
- (Optional) Neo4j AuraDB & Supabase instances or local offline mocks

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 📄 License
This project is licensed under the MIT License. Sample corpus data is derived from CC-BY-SA Wikipedia articles.
