import React from 'react';
import { FileText, X } from 'lucide-react';

interface CitationCardProps {
  chunkId: string;
  onClose: () => void;
}

const SAMPLE_CHUNK_DATA: Record<string, { doc: string; text: string }> = {
  chunk_0000: {
    doc: "wikipedia_ai_acquisitions_1.txt",
    text: "Microsoft Corporation announced a multi-billion dollar investment in OpenAI... Prior to OpenAI, Microsoft acquired Nuance Communications in March 2022 for $19.7 billion to expand its healthcare AI capabilities."
  },
  chunk_0001: {
    doc: "wikipedia_ai_acquisitions_1.txt",
    text: "In 2014, Google acquired DeepMind... In April 2023, Google merged DeepMind with the Google Brain research team to form Google DeepMind, led by Demis Hassabis as CEO."
  },
  chunk_0002: {
    doc: "wikipedia_ai_acquisitions_2.txt",
    text: "In 2013, Meta acquired MobileEye technology assets and hired AI pioneer Yann LeCun to lead FAIR... Meta later acquired Scruffy AI in 2020 and released Llama models."
  },
  chunk_0003: {
    doc: "wikipedia_ai_acquisitions_2.txt",
    text: "In March 2020, Nvidia completed its acquisition of Mellanox Technologies for $6.9 billion... In 2024, Nvidia acquired Run:ai to optimize GPU compute workload."
  },
  chunk_0004: {
    doc: "wikipedia_ai_acquisitions_2.txt",
    text: "Apple Inc. acquired over 30 AI startups... Notable acquisitions include Xnor.ai in 2020 for $200 million, Voicery in 2020, and WaveOne in 2023."
  }
};

export const CitationCard: React.FC<CitationCardProps> = ({ chunkId, onClose }) => {
  const data = SAMPLE_CHUNK_DATA[chunkId] || {
    doc: "source_doc.txt",
    text: `Verified text chunk evidence for [${chunkId}].`
  };

  return (
    <div style={{
      padding: '1rem',
      background: 'rgba(30, 41, 59, 0.95)',
      border: '1px solid var(--accent-purple)',
      borderRadius: '8px',
      marginTop: '0.75rem',
      boxShadow: '0 4px 20px rgba(139, 92, 246, 0.25)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-cyan)', fontSize: '0.85rem' }}>
          <FileText size={16} />
          <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{chunkId}</span>
          <span style={{ color: 'var(--text-muted)' }}>({data.doc})</span>
        </div>
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
          <X size={16} />
        </button>
      </div>
      <p style={{ fontSize: '0.85rem', lineHeight: 1.5, color: '#e2e8f0' }}>"{data.text}"</p>
    </div>
  );
};
