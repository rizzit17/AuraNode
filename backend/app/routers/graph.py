from fastapi import APIRouter
from app.models.graph import SubgraphResponse
from app.services.graph_search import traverse_subgraph

router = APIRouter(prefix="/api/graph", tags=["Graph"])

@router.get("/subgraph", response_model=SubgraphResponse)
def get_full_or_subgraph(entities: str = "", hops: int = 2):
    entity_list = [e.strip() for e in entities.split(",") if e.strip()] if entities else ["Microsoft", "Google", "Meta", "Nvidia", "Apple"]
    subgraph_data = traverse_subgraph(entity_list, hops=hops)
    return SubgraphResponse(
        nodes=subgraph_data["nodes"],
        edges=subgraph_data["edges"],
        traversal_path=subgraph_data["traversal_path"]
    )
