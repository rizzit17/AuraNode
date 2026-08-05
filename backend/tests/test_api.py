import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "AuraNode" in data["service"]

def test_subgraph_endpoint():
    response = client.get("/api/graph/subgraph?entities=Microsoft,Google&hops=2")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert "traversal_path" in data

def test_query_endpoint():
    payload = {
        "question": "What companies did Microsoft acquire in AI?",
        "top_k": 3,
        "hops": 2
    }
    response = client.post("/api/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert "subgraph" in data
    assert data["retrieval_method"] == "hybrid_vector_graph"
