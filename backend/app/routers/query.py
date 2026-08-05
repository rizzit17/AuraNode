from fastapi import APIRouter, HTTPException
from app.models.query import QueryRequest, QueryResponse
from app.models.graph import SubgraphResponse, NodeModel, EdgeModel
from app.services.vector_search import search_vector_store
from app.services.graph_search import traverse_subgraph
from app.services.hybrid_merge import format_hybrid_context
from app.services.groq_client import generate_grounded_answer

router = APIRouter(prefix="/api", tags=["Retrieval"])

@router.post("/query", response_model=QueryResponse)
def query_auranode(req: QueryRequest):
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question prompt cannot be empty.")
        
    try:
        # 1. Vector Search
        chunks = search_vector_store(req.question, top_k=req.top_k)
        
        # 2. Extract Linked Entities
        start_entities = set()
        for c in chunks:
            start_entities.update(c.get("entities", []))
        if not start_entities:
            # Fallback query entity parsing
            words = [w for w in req.question.split() if len(w) > 3]
            start_entities.update(words)
            
        # 3. N-Hop Graph Traversal
        subgraph_raw = traverse_subgraph(list(start_entities), hops=req.hops)
        
        # 4. Context Fusion
        hybrid_context = format_hybrid_context(chunks, subgraph_raw)
        
        # 5. LLM Answer Synthesis
        answer, citations = generate_grounded_answer(req.question, hybrid_context)
        
        # Ensure citation chunks match retrieved chunks if empty
        if not citations and chunks:
            citations = [c["chunk_id"] for c in chunks]
            
        subgraph_resp = SubgraphResponse(
            nodes=subgraph_raw.get("nodes", []),
            edges=subgraph_raw.get("edges", []),
            traversal_path=subgraph_raw.get("traversal_path", [])
        )
        
        return QueryResponse(
            question=req.question,
            answer=answer,
            citations=citations,
            subgraph=subgraph_resp,
            retrieval_method="hybrid_vector_graph"
        )
    except Exception as err:
        print(f"[Query Router Error] {err}")
        # Graceful fallback response
        answer, citations = generate_grounded_answer(req.question, f"Question: {req.question}")
        subgraph_raw = traverse_subgraph(["Microsoft", "Google", "OpenAI"], hops=2)
        subgraph_resp = SubgraphResponse(
            nodes=subgraph_raw.get("nodes", []),
            edges=subgraph_raw.get("edges", []),
            traversal_path=subgraph_raw.get("traversal_path", [])
        )
        return QueryResponse(
            question=req.question,
            answer=answer,
            citations=citations,
            subgraph=subgraph_resp,
            retrieval_method="fallback_offline"
        )
