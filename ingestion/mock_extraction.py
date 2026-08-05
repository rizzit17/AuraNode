import os
import json
import glob
import re

RAW_DIR = os.path.join(os.path.dirname(__file__), "sample_data", "raw")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_data")

def chunk_text(text: str, max_chars: int = 500) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) + 2 <= max_chars:
            current_chunk = f"{current_chunk}\n\n{p}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = p
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def extract_triplets_from_chunk(text: str, chunk_id: str) -> list[dict]:
    # Rule-based/regex extraction for deterministic offline mock dataset generation
    triplets = []
    
    patterns = [
        (r"(Microsoft)\s+announced a multi-billion dollar investment in\s+(OpenAI)", "Microsoft", "COMPANY", "invested in", "OpenAI", "ORGANIZATION"),
        (r"(Microsoft)\s+acquired\s+(Nuance Communications)", "Microsoft", "COMPANY", "acquired", "Nuance Communications", "COMPANY"),
        (r"(Google)\s+acquired\s+(DeepMind)", "Google", "COMPANY", "purchased", "DeepMind", "ORGANIZATION"),
        (r"(Google)\s+merged DeepMind with the (Google Brain)", "Google", "COMPANY", "merged with", "Google Brain", "ORGANIZATION"),
        (r"(Demis Hassabis)\s+as CEO", "Demis Hassabis", "PERSON", "leads", "Google DeepMind", "ORGANIZATION"),
        (r"(Google)\s+acquired\s+(Kaggle)", "Google", "COMPANY", "bought", "Kaggle", "ORGANIZATION"),
        (r"(Meta)\s+acquired\s+(MobileEye)", "Meta", "COMPANY", "bought out", "MobileEye", "COMPANY"),
        (r"(Yann LeCun)\s+to lead\s+(FAIR)", "Yann LeCun", "PERSON", "directs", "FAIR", "ORGANIZATION"),
        (r"(Meta)\s+acquired\s+(Scruffy AI)", "Meta", "COMPANY", "acquired", "Scruffy AI", "COMPANY"),
        (r"(Meta)\s+released the open-source\s+(Llama)", "Meta", "COMPANY", "developed", "Llama", "MODEL"),
        (r"(Nvidia)\s+completed its acquisition of\s+(Mellanox Technologies)", "Nvidia", "COMPANY", "bought", "Mellanox Technologies", "COMPANY"),
        (r"(Nvidia)\s+attempted to acquire\s+(ARM Holdings)", "Nvidia", "COMPANY", "attempted acquisition of", "ARM Holdings", "COMPANY"),
        (r"(Nvidia)\s+acquired\s+(Run:ai)", "Nvidia", "COMPANY", "purchased", "Run:ai", "COMPANY"),
        (r"(Apple)\s+acquired over 30 AI startups", "Apple", "COMPANY", "acquired", "AI Startups", "CATEGORY"),
        (r"(Apple)\s+acquired\s+(Xnor.ai)", "Apple", "COMPANY", "bought out", "Xnor.ai", "COMPANY"),
        (r"(Apple)\s+acquired\s+(Voicery)", "Apple", "COMPANY", "purchased", "Voicery", "COMPANY"),
        (r"(Apple)\s+acquired\s+(WaveOne)", "Apple", "COMPANY", "bought", "WaveOne", "COMPANY"),
    ]
    
    for pattern, s, st, rel, o, ot in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            triplets.append({
                "chunk_id": chunk_id,
                "subject": s,
                "subject_type": st,
                "relation": rel,
                "object": o,
                "object_type": ot
            })
            
    return triplets

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    raw_files = glob.glob(os.path.join(RAW_DIR, "*.txt"))
    print(f"[Offline Extraction] Found {len(raw_files)} raw text files.")
    
    all_chunks = []
    all_triplets = []
    chunk_counter = 0
    
    for filepath in raw_files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        chunks = chunk_text(content)
        for chunk_str in chunks:
            cid = f"chunk_{chunk_counter:04d}"
            chunk_obj = {
                "chunk_id": cid,
                "source_doc": filename,
                "text": chunk_str
            }
            all_chunks.append(chunk_obj)
            
            triplets = extract_triplets_from_chunk(chunk_str, cid)
            all_triplets.extend(triplets)
            chunk_counter += 1
            
    # Write chunks.jsonl
    chunks_path = os.path.join(OUTPUT_DIR, "chunks.jsonl")
    with open(chunks_path, "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c) + "\n")
            
    # Write triplets.jsonl
    triplets_path = os.path.join(OUTPUT_DIR, "triplets.jsonl")
    with open(triplets_path, "w", encoding="utf-8") as f:
        for t in all_triplets:
            f.write(json.dumps(t) + "\n")
            
    print(f"[Offline Extraction] Complete!")
    print(f"  - Generated {len(all_chunks)} chunks -> {chunks_path}")
    print(f"  - Extracted {len(all_triplets)} triplets -> {triplets_path}")

if __name__ == "__main__":
    main()
