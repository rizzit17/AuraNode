import React, { useState } from 'react';
import { SubgraphData } from '../api/client';
import { Network, Layers, Layout, Grid } from 'lucide-react';
import ForceGraph2D from 'react-force-graph-2d';

interface GraphViewProps {
  subgraph: SubgraphData | null;
}

export const GraphView: React.FC<GraphViewProps> = ({ subgraph }) => {
  const [viewMode, setViewMode] = useState<'force' | 'schematic'>('force');
  const nodes = subgraph?.nodes || [];
  const edges = subgraph?.edges || [];

  // Format nodes and links for react-force-graph-2d
  const graphData = {
    nodes: nodes.map(n => ({
      id: n.id,
      name: n.label,
      type: n.type,
      val: subgraph?.traversal_path.includes(n.id) ? 12 : 7
    })),
    links: edges.map(e => ({
      source: e.source,
      target: e.target,
      relation: e.relation,
      is_traversed: e.is_traversed
    }))
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid var(--ink)', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Network size={20} color="var(--signal)" />
          <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.35rem', color: 'var(--ink)' }}>
            REASONING TRACE
          </h2>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {/* View Toggle */}
          <div style={{ display: 'flex', border: '2px solid var(--ink)', background: 'var(--paper)', borderRadius: '4px', overflow: 'hidden' }}>
            <button
              onClick={() => setViewMode('force')}
              style={{
                padding: '0.25rem 0.6rem',
                border: 'none',
                background: viewMode === 'force' ? 'var(--signal)' : 'transparent',
                color: viewMode === 'force' ? 'var(--paper)' : 'var(--ink)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.75rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem'
              }}
            >
              <Layout size={14} /> 2D FORCE
            </button>
            <button
              onClick={() => setViewMode('schematic')}
              style={{
                padding: '0.25rem 0.6rem',
                border: 'none',
                borderLeft: '1px solid var(--ink)',
                background: viewMode === 'schematic' ? 'var(--signal)' : 'transparent',
                color: viewMode === 'schematic' ? 'var(--paper)' : 'var(--ink)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.75rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem'
              }}
            >
              <Grid size={14} /> SCHEMATIC
            </button>
          </div>

          <span className="status-badge">
            <Layers size={14} />
            {nodes.length} NODES / {edges.length} EDGES
          </span>
        </div>
      </div>

      {/* Graph Paper Canvas Container */}
      <div style={{ flex: 1, position: 'relative', marginTop: '1rem', border: '2px solid var(--ink)', background: 'var(--card)', boxShadow: 'var(--shadow-panel)', overflow: 'hidden' }}>
        {nodes.length === 0 ? (
          <div style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', color: 'var(--ink-soft)' }}>
            <Network size={48} strokeWidth={1.5} />
            <p style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', marginTop: '1rem' }}>No Subgraph Traversed Yet</p>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>Ask a question to trigger vector + 2-hop graph reasoning</p>
          </div>
        ) : (
          <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Traversed Path Legend */}
            <div style={{ padding: '0.75rem 1rem', borderBottom: '2px solid var(--ink)', background: 'var(--paper)', display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', fontWeight: 700, color: 'var(--signal)' }}>
                ⚡ TRAVERSED REASONING PATHWAY:
              </span>
              {subgraph?.traversal_path.map((entity, idx) => (
                <span key={idx} style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', background: 'var(--signal)', color: 'var(--paper)', padding: '0.2rem 0.6rem', border: '1px solid var(--ink)', boxShadow: '1px 1px 0 var(--ink)' }}>
                  {idx + 1}. {entity}
                </span>
              ))}
            </div>

            <div style={{ flex: 1, position: 'relative', overflow: 'auto' }}>
              {viewMode === 'force' ? (
                <ForceGraph2D
                  graphData={graphData}
                  nodeLabel={(n: any) => `${n.name} [${n.type}]`}
                  nodeColor={(n: any) => subgraph?.traversal_path.includes(n.id) ? '#2447FF' : '#14161A'}
                  linkColor={(l: any) => l.is_traversed ? '#2447FF' : '#D8D8CC'}
                  linkWidth={(l: any) => l.is_traversed ? 3 : 1}
                  linkLabel={(l: any) => l.relation}
                  linkDirectionalParticles={(l: any) => l.is_traversed ? 4 : 0}
                  linkDirectionalParticleSpeed={0.005}
                  backgroundColor="#FFFFFF"
                />
              ) : (
                <div style={{ padding: '1.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                  {edges.map((edge, idx) => (
                    <div 
                      key={idx} 
                      style={{
                        border: '2px solid var(--ink)',
                        background: edge.is_traversed ? 'var(--paper)' : 'var(--card)',
                        boxShadow: edge.is_traversed ? 'var(--shadow-chip)' : 'none',
                        padding: '0.85rem'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', fontWeight: 700, color: 'var(--ink)' }}>
                          {edge.source}
                        </span>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem', background: 'var(--signal)', color: 'var(--paper)', padding: '0.15rem 0.4rem' }}>
                          {edge.relation}
                        </span>
                      </div>
                      
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', fontWeight: 700, color: 'var(--ink)' }}>
                          ➔ {edge.target}
                        </span>
                        {edge.chunk_id && (
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.65rem', color: 'var(--ink-soft)' }}>
                            [{edge.chunk_id}]
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
