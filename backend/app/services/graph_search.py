import os
import json

SAMPLE_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ingestion", "sample_data"))
GRAPH_FILE = os.path.join(SAMPLE_DATA_DIR, "graph_db.json")

def traverse_subgraph(start_entities: list[str], hops: int = 2) -> dict:
    if not os.path.exists(GRAPH_FILE):
        return {"nodes": [], "edges": [], "traversal_path": []}
        
    with open(GRAPH_FILE, "r", encoding="utf-8") as f:
        graph_data = json.load(f)
        
    all_nodes = {n["id"]: n for n in graph_data.get("nodes", [])}
    all_edges = graph_data.get("edges", [])
    
    # Matching start entities (case-insensitive fuzzy match)
    visited_nodes = set()
    for entity in start_entities:
        for nid in all_nodes:
            if entity.lower() in nid.lower() or nid.lower() in entity.lower():
                visited_nodes.add(nid)
                
    current_frontier = set(visited_nodes)
    traversed_edges = []
    traversal_path = list(visited_nodes)
    
    for hop in range(hops):
        next_frontier = set()
        for edge in all_edges:
            src = edge["source"]
            tgt = edge["target"]
            if src in current_frontier or tgt in current_frontier:
                if edge not in traversed_edges:
                    traversed_edges.append(edge)
                if src in current_frontier and tgt not in visited_nodes:
                    next_frontier.add(tgt)
                    visited_nodes.add(tgt)
                    traversal_path.append(tgt)
                elif tgt in current_frontier and src not in visited_nodes:
                    next_frontier.add(src)
                    visited_nodes.add(src)
                    traversal_path.append(src)
        current_frontier = next_frontier
        
    res_nodes = [all_nodes[nid] for nid in visited_nodes if nid in all_nodes]
    
    # Form edge models
    formatted_edges = []
    for e in traversed_edges:
        formatted_edges.append({
            "source": e["source"],
            "target": e["target"],
            "relation": e["relation"],
            "raw_relation": e.get("raw_relation"),
            "chunk_id": e.get("chunk_id"),
            "is_traversed": True
        })
        
    return {
        "nodes": res_nodes,
        "edges": formatted_edges,
        "traversal_path": traversal_path
    }
