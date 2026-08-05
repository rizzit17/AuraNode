import os
import json

def load_dotenv_root():
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_dotenv_root()

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
TRIPLETS_FILE = os.path.join(SAMPLE_DATA_DIR, "triplets.jsonl")
SCHEMA_FILE = os.path.join(SAMPLE_DATA_DIR, "schema.json")
GRAPH_EXPORT_FILE = os.path.join(SAMPLE_DATA_DIR, "graph_db.json")

def load_schema():
    if os.path.exists(SCHEMA_FILE):
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"relation_mapping": {}}

def load_graph():
    schema = load_schema()
    rel_map = schema.get("relation_mapping", {})
    
    nodes_dict = {}
    edges_list = []
    
    if not os.path.exists(TRIPLETS_FILE):
        print("Triplets file missing.")
        return
        
    with open(TRIPLETS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            t = json.loads(line)
            s_name = t["subject"]
            s_type = t.get("subject_type", "ENTITY")
            o_name = t["object"]
            o_type = t.get("object_type", "ENTITY")
            raw_rel = t["relation"]
            canon_rel = rel_map.get(raw_rel, raw_rel.upper().replace(" ", "_"))
            cid = t.get("chunk_id", "")
            
            # Nodes
            if s_name not in nodes_dict:
                nodes_dict[s_name] = {"id": s_name, "label": s_name, "type": s_type}
            if o_name not in nodes_dict:
                nodes_dict[o_name] = {"id": o_name, "label": o_name, "type": o_type}
                
            # Edge
            edges_list.append({
                "source": s_name,
                "target": o_name,
                "relation": canon_rel,
                "raw_relation": raw_rel,
                "chunk_id": cid
            })
            
    # Try Neo4j connection if creds provided
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USERNAME")
    neo4j_pass = os.getenv("NEO4J_PASSWORD")
    
    if neo4j_uri and neo4j_pass:
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
            with driver.session() as session:
                for n in nodes_dict.values():
                    cypher_node = "MERGE (e:Entity {id: $id}) SET e.label = $label, e.type = $type"
                    session.run(cypher_node, id=n["id"], label=n["label"], type=n["type"])
                for e in edges_list:
                    cypher_edge = (
                        "MATCH (a:Entity {id: $source}), (b:Entity {id: $target}) "
                        f"MERGE (a)-[r:{e['relation']}]->(b) "
                        "SET r.chunk_id = $chunk_id"
                    )
                    session.run(cypher_edge, source=e["source"], target=e["target"], chunk_id=e["chunk_id"])
            print("[Graph Load] Successfully ingested nodes and edges into Neo4j AuraDB!")
        except Exception as err:
            print(f"[Graph Load] Neo4j connection skipped/failed: {err}. Using local graph export.")
    else:
        print("[Graph Load] Neo4j credentials not set. Exporting to local JSON graph database.")
        
    # Always write local graph snapshot for offline testing
    graph_payload = {
        "nodes": list(nodes_dict.values()),
        "edges": edges_list
    }
    with open(GRAPH_EXPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(graph_payload, f, indent=2)
    print(f"[Graph Load] Exported {len(nodes_dict)} nodes and {len(edges_list)} edges -> {GRAPH_EXPORT_FILE}")

if __name__ == "__main__":
    load_graph()
