from pydantic import BaseModel
from typing import List
from app.models.graph import SubgraphResponse

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3
    hops: int = 2

class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[str]
    subgraph: SubgraphResponse
    retrieval_method: str = "hybrid_vector_graph"
