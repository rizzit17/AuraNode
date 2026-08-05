def format_hybrid_context(vector_chunks: list[dict], graph_subgraph: dict) -> str:
    context_parts = []
    
    # 1. Text Evidence (Vector Chunks)
    context_parts.append("=== TEXT EVIDENCE (Vector Similarity Chunks) ===")
    if not vector_chunks:
        context_parts.append("No direct text evidence found.")
    else:
        for idx, chunk in enumerate(vector_chunks, 1):
            cid = chunk.get("chunk_id", f"chunk_{idx}")
            doc = chunk.get("source_doc", "unknown")
            text = chunk.get("text", "")
            context_parts.append(f"[{cid}] (Source: {doc}):\n\"{text}\"\n")
            
    # 2. Graph Relationship Evidence (Sub_graph Traversal)
    context_parts.append("=== KNOWLEDGE GRAPH RELATIONSHIPS (2-Hop Traversal) ===")
    edges = graph_subgraph.get("edges", [])
    if not edges:
        context_parts.append("No graph relationship paths retrieved.")
    else:
        for edge in edges:
            src = edge.get("source", "")
            rel = edge.get("relation", "")
            tgt = edge.get("target", "")
            cid = edge.get("chunk_id", "")
            cite = f" [{cid}]" if cid else ""
            context_parts.append(f"- ({src}) --[{rel}]--> ({tgt}){cite}")
            
    return "\n".join(context_parts)
