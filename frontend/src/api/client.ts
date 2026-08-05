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

const BACKEND_TARGETS = [
  '/api',
  'http://localhost:8000/api',
  'http://localhost:8001/api',
  'http://localhost:8002/api',
  'http://127.0.0.1:8000/api',
  'http://127.0.0.1:8001/api'
];

export async function sendQuery(question: string, topK: number = 3, hops: number = 2): Promise<QueryResponse> {
  let lastError: Error | null = null;

  for (const baseUrl of BACKEND_TARGETS) {
    try {
      const response = await fetch(`${baseUrl}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, top_k: topK, hops })
      });
      if (response.ok) {
        return await response.json();
      }
    } catch (err: any) {
      lastError = err;
    }
  }

  throw lastError || new Error("Unable to connect to AuraNode backend server.");
}

export async function fetchSubgraph(entities: string = '', hops: number = 2): Promise<SubgraphData> {
  const queryParam = `?entities=${encodeURIComponent(entities)}&hops=${hops}`;
  
  for (const baseUrl of BACKEND_TARGETS) {
    try {
      const response = await fetch(`${baseUrl}/graph/subgraph${queryParam}`);
      if (response.ok) {
        return await response.json();
      }
    } catch (err) {
      // Continue to next fallback
    }
  }

  return { nodes: [], edges: [], traversal_path: [] };
}
