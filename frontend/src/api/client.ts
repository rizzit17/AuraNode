export interface Node {
  id: string;
  label: string;
  type: string;
}

export interface Edge {
  source: string;
  target: string;
  relation: string;
  raw_relation?: string;
  chunk_id?: string;
  is_traversed: boolean;
}

export interface SubgraphData {
  nodes: Node[];
  edges: Edge[];
  traversal_path: string[];
}

export interface QueryResponse {
  question: string;
  answer: string;
  citations: string[];
  subgraph: SubgraphData;
  retrieval_method: string;
}

export async function sendQuery(question: string, topK: number = 3, hops: number = 2): Promise<QueryResponse> {
  const response = await fetch('/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: topK, hops })
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchSubgraph(entities: string = '', hops: number = 2): Promise<SubgraphData> {
  const response = await fetch(`/api/graph/subgraph?entities=${encodeURIComponent(entities)}&hops=${hops}`);
  if (!response.ok) {
    throw new Error(`Graph API error: ${response.statusText}`);
  }
  return response.json();
}
