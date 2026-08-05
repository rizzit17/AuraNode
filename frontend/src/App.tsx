import React, { useState, useEffect } from 'react';
import { ChatPanel } from './components/ChatPanel';
import { GraphView } from './components/GraphView';
import { sendQuery, fetchSubgraph, SubgraphData } from './api/client';
import { Database, Cpu, CheckCircle2 } from 'lucide-react';

interface Message {
  id: string;
  sender: 'user' | 'auranode';
  text: string;
  citations?: string[];
}

export const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [subgraph, setSubgraph] = useState<SubgraphData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Initial fetch of full subgraph schema on load
    fetchSubgraph()
      .then((data) => setSubgraph(data))
      .catch((err) => console.log("Initial subgraph load notice:", err));
  }, []);

  const handleSendMessage = async (queryText: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: queryText
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const response = await sendQuery(queryText);
      const auranodeMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'auranode',
        text: response.answer,
        citations: response.citations
      };
      setMessages((prev) => [...prev, auranodeMsg]);
      setSubgraph(response.subgraph);
    } catch (err) {
      console.error("Query Error:", err);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'auranode',
        text: "Error executing query against AuraNode hybrid backend. Please check backend server status."
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header Bar */}
      <header className="app-header">
        <div className="brand-logo">
          <Database size={24} color="var(--paper)" />
          <span>AURANODE</span>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--paper-line)' }}>
            <Cpu size={16} />
            <span>SCHEMA: 5 CANONICAL TYPES</span>
          </div>
          
          <div className="status-badge">
            <CheckCircle2 size={14} color="var(--edge-live)" />
            <span>BACKEND ONLINE</span>
          </div>
        </div>
      </header>

      {/* Split Dashboard */}
      <main className="main-content">
        <section className="chat-section">
          <ChatPanel 
            messages={messages} 
            onSendMessage={handleSendMessage} 
            loading={loading} 
          />
        </section>
        
        <section className="graph-section">
          <GraphView subgraph={subgraph} />
        </section>
      </main>
    </div>
  );
};

export default App;
