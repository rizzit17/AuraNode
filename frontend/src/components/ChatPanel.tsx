import React, { useState } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { CitationCard } from './CitationCard';

interface Message {
  id: string;
  sender: 'user' | 'auranode';
  text: string;
  citations?: string[];
}

interface ChatPanelProps {
  messages: Message[];
  onSendMessage: (query: string) => void;
  loading: boolean;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ messages, onSendMessage, loading }) => {
  const [inputQuery, setInputQuery] = useState('');
  const [selectedCitation, setSelectedCitation] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputQuery.trim() || loading) return;
    onSendMessage(inputQuery);
    setInputQuery('');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '1rem', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid var(--ink)', paddingBottom: '0.75rem' }}>
        <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.35rem', color: 'var(--ink)' }}>
          ASK AURANODE
        </h2>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--ink-soft)', textTransform: 'uppercase' }}>
          HYBRID RETRIEVAL v1.0
        </span>
      </div>

      {/* Message List */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem', paddingRight: '0.25rem' }}>
        {messages.length === 0 ? (
          <div className="neobrutal-card" style={{ marginTop: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--signal)' }}>
              <Sparkles size={20} />
              <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem' }}>Demo Knowledge Graph Active</h3>
            </div>
            <p style={{ fontSize: '0.9rem', lineHeight: 1.5, color: 'var(--ink-soft)' }}>
              AuraNode has ingested CC-BY-SA public data on <strong>AI Industry Acquisitions & Ecosystem Partnerships</strong> (Microsoft/OpenAI, Google/DeepMind, Meta, Nvidia, Apple).
            </p>
            <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--ink-soft)' }}>TRY ASKING:</span>
              <button 
                onClick={() => onSendMessage("What companies did Microsoft acquire in AI?")}
                style={{ textAlign: 'left', padding: '0.5rem', border: '1px solid var(--ink)', background: 'var(--paper)', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}
              >
                ➔ What companies did Microsoft acquire in AI?
              </button>
              <button 
                onClick={() => onSendMessage("Who leads Google DeepMind and what did Google acquire?")}
                style={{ textAlign: 'left', padding: '0.5rem', border: '1px solid var(--ink)', background: 'var(--paper)', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}
              >
                ➔ Who leads Google DeepMind and what did Google acquire?
              </button>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div 
              key={msg.id}
              style={{
                alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '85%'
              }}
            >
              {msg.sender === 'user' ? (
                <div style={{
                  background: 'var(--ink)',
                  color: 'var(--paper)',
                  padding: '0.75rem 1rem',
                  border: '2px solid var(--ink)',
                  boxShadow: 'var(--shadow-chip)',
                  fontFamily: 'var(--font-body)',
                  fontSize: '0.95rem'
                }}>
                  {msg.text}
                </div>
              ) : (
                <div className="neobrutal-card">
                  <p style={{ fontSize: '0.95rem', lineHeight: 1.6, color: 'var(--ink)' }}>{msg.text}</p>
                  
                  {msg.citations && msg.citations.length > 0 && (
                    <div style={{ marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid var(--paper-line)', display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.4rem' }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem', color: 'var(--ink-soft)' }}>SOURCES:</span>
                      {msg.citations.map((cite) => (
                        <button
                          key={cite}
                          className="node-chip"
                          onClick={() => setSelectedCitation(selectedCitation === cite ? null : cite)}
                        >
                          <div className="node-chip-stripe" style={{ background: 'var(--signal)' }}></div>
                          <div className="node-chip-body">
                            <span className="node-chip-label">{cite}</span>
                            <span className="node-chip-type">CHUNK</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  )}

                  {selectedCitation && (
                    <CitationCard chunkId={selectedCitation} onClose={() => setSelectedCitation(null)} />
                  )}
                </div>
              )}
            </div>
          ))
        )}

        {loading && (
          <div className="neobrutal-card" style={{ alignSelf: 'flex-start', borderColor: 'var(--current)' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: 'var(--ink)' }}>
              ⚡ Querying pgvector + 2-hop Neo4j traversal...
            </span>
          </div>
        )}
      </div>

      {/* Input Box */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem', marginTop: 'auto' }}>
        <input 
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder="Ask AuraNode a question..."
          disabled={loading}
          style={{
            flex: 1,
            padding: '0.75rem 1rem',
            border: '2px solid var(--ink)',
            background: 'var(--card)',
            fontFamily: 'var(--font-body)',
            fontSize: '0.95rem',
            outline: 'none'
          }}
        />
        <button type="submit" disabled={loading} className="btn-signal" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Send size={16} />
          ASK
        </button>
      </form>
    </div>
  );
};
