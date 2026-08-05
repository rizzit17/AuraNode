import os
import json
import math

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
CHUNKS_FILE = os.path.join(SAMPLE_DATA_DIR, "chunks.jsonl")
TRIPLETS_FILE = os.path.join(SAMPLE_DATA_DIR, "triplets.jsonl")
VECTOR_STORE_FILE = os.path.join(SAMPLE_DATA_DIR, "vector_store.json")

def dummy_text_embedding(text: str, dim: int = 384) -> list[float]:
    # Deterministic fallback embedding based on token hashing if sentence-transformers is offline
    vec = [0.0] * dim
    words = text.lower().split()
    for w in words:
        h = sum(ord(c) for c in w)
        idx = h % dim
        vec[idx] += 1.0
    norm = math.sqrt(sum(v*v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec

_MODEL_INSTANCE = None

def get_embedding(text: str) -> list[float]:
    global _MODEL_INSTANCE
    try:
        if _MODEL_INSTANCE is None:
            from sentence_transformers import SentenceTransformer
            _MODEL_INSTANCE = SentenceTransformer("all-MiniLM-L6-v2")
        return _MODEL_INSTANCE.encode(text).tolist()
    except Exception:
        return dummy_text_embedding(text)

def embed_chunks():
    if not os.path.exists(CHUNKS_FILE):
        print("Chunks file missing. Run mock_extraction.py first.")
        return
        
    chunk_to_entities = {}
    if os.path.exists(TRIPLETS_FILE):
        with open(TRIPLETS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    t = json.loads(line)
                    cid = t.get("chunk_id")
                    if cid:
                        if cid not in chunk_to_entities:
                            chunk_to_entities[cid] = set()
                        chunk_to_entities[cid].add(t["subject"])
                        chunk_to_entities[cid].add(t["object"])
                        
    records = []
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            chunk = json.loads(line)
            cid = chunk["chunk_id"]
            text = chunk["text"]
            source = chunk.get("source_doc", "")
            linked_entities = list(chunk_to_entities.get(cid, []))
            
            vector = get_embedding(text)
            records.append({
                "chunk_id": cid,
                "text": text,
                "source_doc": source,
                "entities": linked_entities,
                "vector": vector
            })
            
    with open(VECTOR_STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
        
    print(f"[Vector Ingestion] Successfully embedded {len(records)} chunks -> {VECTOR_STORE_FILE}")

if __name__ == "__main__":
    embed_chunks()
