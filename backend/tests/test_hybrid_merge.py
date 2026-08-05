import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.hybrid_merge import format_hybrid_context

def test_format_hybrid_context():
    vector_chunks = [
        {"chunk_id": "chunk_0001", "source_doc": "test.txt", "text": "Microsoft acquired Nuance Communications."}
    ]
    graph_subgraph = {
        "edges": [
            {"source": "Microsoft", "relation": "ACQUIRED", "target": "Nuance Communications", "chunk_id": "chunk_0001"}
        ]
    }
    
    formatted = format_hybrid_context(vector_chunks, graph_subgraph)
    assert "=== TEXT EVIDENCE" in formatted
    assert "=== KNOWLEDGE GRAPH RELATIONSHIPS" in formatted
    assert "Microsoft acquired Nuance Communications" in formatted
    assert "(Microsoft) --[ACQUIRED]--> (Nuance Communications) [chunk_0001]" in formatted
