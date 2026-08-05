from pydantic import BaseModel
from typing import List, Optional

class NodeModel(BaseModel):
    id: str
    label: str
    type: str

class EdgeModel(BaseModel):
    source: str
    target: str
    relation: str
    raw_relation: Optional[str] = None
    chunk_id: Optional[str] = None
    is_traversed: bool = True

class SubgraphResponse(BaseModel):
    nodes: List[NodeModel]
    edges: List[EdgeModel]
    traversal_path: List[str]
