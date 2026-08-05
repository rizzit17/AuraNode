import os
import json
from collections import defaultdict

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
TRIPLETS_FILE = os.path.join(SAMPLE_DATA_DIR, "triplets.jsonl")
SCHEMA_FILE = os.path.join(SAMPLE_DATA_DIR, "schema.json")
METRICS_FILE = os.path.join(SAMPLE_DATA_DIR, "schema_metrics.json")

def normalize_label(label: str) -> str:
    return label.strip().lower()

def canonicalize_label(label: str) -> str:
    clean = normalize_label(label)
    # Semantic mapping clusters
    synonyms = {
        "acquired": "ACQUIRED",
        "bought": "ACQUIRED",
        "purchased": "ACQUIRED",
        "bought out": "ACQUIRED",
        "attempted acquisition of": "ACQUIRED",
        "invested in": "INVESTED_IN",
        "merged with": "MERGED_WITH",
        "leads": "LEADS",
        "directs": "LEADS",
        "developed": "DEVELOPED"
    }
    return synonyms.get(clean, clean.upper().replace(" ", "_"))

def discover_schema():
    if not os.path.exists(TRIPLETS_FILE):
        raise FileNotFoundError(f"Triplets file not found at {TRIPLETS_FILE}. Run mock_extraction.py first.")
        
    raw_triplets = []
    with open(TRIPLETS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                raw_triplets.append(json.loads(line))
                
    raw_relation_labels = set()
    raw_subject_types = set()
    raw_object_types = set()
    
    relation_mapping = {}
    canonical_relations = set()
    
    for t in raw_triplets:
        rel = t.get("relation", "")
        st = t.get("subject_type", "")
        ot = t.get("object_type", "")
        
        raw_relation_labels.add(rel)
        if st:
            raw_subject_types.add(st)
        if ot:
            raw_object_types.add(ot)
            
        canonical_rel = canonicalize_label(rel)
        relation_mapping[rel] = canonical_rel
        canonical_relations.add(canonical_rel)
        
    schema_data = {
        "relation_mapping": relation_mapping,
        "canonical_relations": list(canonical_relations),
        "entity_types": list(raw_subject_types.union(raw_object_types))
    }
    
    with open(SCHEMA_FILE, "w", encoding="utf-8") as f:
        json.dump(schema_data, f, indent=2)
        
    # Calculate quantitative schema reduction metrics
    raw_rel_count = len(raw_relation_labels)
    canonical_rel_count = len(canonical_relations)
    reduction_pct = round(((raw_rel_count - canonical_rel_count) / raw_rel_count) * 100, 2) if raw_rel_count > 0 else 0.0
    
    metrics_data = {
        "total_triplets_processed": len(raw_triplets),
        "raw_relation_labels_count": raw_rel_count,
        "canonical_relations_count": canonical_rel_count,
        "schema_reduction_percentage": f"{reduction_pct}%",
        "sample_clusters": {
            "ACQUIRED": [r for r, c in relation_mapping.items() if c == "ACQUIRED"],
            "INVESTED_IN": [r for r, c in relation_mapping.items() if c == "INVESTED_IN"]
        }
    }
    
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
        
    print("=== Auto-Schema Discovery Metrics ===")
    print(f"  Processed Triplets: {len(raw_triplets)}")
    print(f"  Raw Relation Labels: {raw_rel_count} -> Canonical Relations: {canonical_rel_count}")
    print(f"  Schema Compression Rate: {reduction_pct}%")
    print(f"  Saved Schema -> {SCHEMA_FILE}")
    print(f"  Saved Metrics -> {METRICS_FILE}")
    return schema_data, metrics_data

if __name__ == "__main__":
    discover_schema()
