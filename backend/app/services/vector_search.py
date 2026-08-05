import os
import json
import math

SAMPLE_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ingestion", "sample_data"))
VECTOR_STORE_FILE = os.path.join(SAMPLE_DATA_DIR, "vector_store.json")

_MODEL_INSTANCE = None

def get_query_embedding(text: str, dim: int = 384) -> list[float]:
    global _MODEL_INSTANCE
    try:
        if _MODEL_INSTANCE is None:
            from sentence_transformers import SentenceTransformer
            _MODEL_INSTANCE = SentenceTransformer("all-MiniLM-L6-v2")
        return _MODEL_INSTANCE.encode(text).tolist()
    except Exception:
        # Fallback keyword matching vector
        vec = [0.0] * dim
        for w in text.lower().split():
            h = sum(ord(c) for c in w)
            vec[h % dim] += 1.0
        norm = math.sqrt(sum(v*v for v in vec))
        return [v/norm for v in vec] if norm > 0 else vec

def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a*b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a*a for a in v1))
    n2 = math.sqrt(sum(b*b for b in v2))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)

def search_vector_store(query: str, top_k: int = 3) -> list[dict]:
    if not os.path.exists(VECTOR_STORE_FILE):
        return []
        
    with open(VECTOR_STORE_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        
    q_vec = get_query_embedding(query)
    
    scored_chunks = []
    for chunk in chunks:
        score = cosine_similarity(q_vec, chunk.get("vector", []))
        scored_chunks.append({
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "source_doc": chunk.get("source_doc", ""),
            "entities": chunk.get("entities", []),
            "score": float(score)
        })
        
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    return scored_chunks[:top_k]
