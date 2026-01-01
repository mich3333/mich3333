import { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { FloatingParticles } from '../components/FloatingParticles';
import { StatusBadge } from '../components/StatusBadge';
import { AgentCard } from '../components/AgentCard';
import { TaskInput } from '../components/TaskInput';
import { LogViewer } from '../components/LogViewer';
import { ResultsPanel } from '../components/ResultsPanel';
import type { Agent } from '../types';
import { useAuth } from '../contexts/AuthContext';

// Configure server URL - change this based on environment
const SERVER_URL = import.meta.env.VITE_SERVER_URL || 'http://localhost:5000';

export const Dashboard = () => {
  const { connected, executeTask, agentUpdates, result, isExecuting } = useWebSocket(SERVER_URL);
  const { user, signOut } = useAuth();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);

  const handleLogout = async () => {
    await signOut();
  };

  // Load agents on mount
  useEffect(() => {
    fetch(`${SERVER_URL}/agents`)
      .then((res) => res.json())
      .then((data) => setAgents(data.agents))
      .catch((err) => console.error('Failed to load agents:', err));
  }, []);

  // Track active agent from updates
  useEffect(() => {
    if (agentUpdates.length > 0) {
      const lastUpdate = agentUpdates[agentUpdates.length - 1];
      setActiveAgent(lastUpdate.agent);

      // Clear active state after 1 second
      const timer = setTimeout(() => setActiveAgent(null), 1000);
      return () => clearTimeout(timer);
    }
  }, [agentUpdates]);

  return (
    <div className="min-h-screen relative">
      <FloatingParticles />

      <div className="relative z-10 container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <header className="mb-12">
          <div className="flex justify-between items-center mb-8">
            <div className="flex items-center gap-3">
              <div className="glass px-4 py-2 rounded-full">
                <span className="text-sm text-gray-400">👤 {user?.email}</span>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="glass px-6 py-2 rounded-full hover:border-red-500/50 border border-white/10 transition-all text-sm"
            >
              🚪 Logout
            </button>
          </div>

          <div className="text-center">
            <h1 className="text-6xl md:text-7xl font-black mb-4 bg-gradient-to-r from-purple-400 via-pink-500 to-purple-600 bg-clip-text text-transparent animate-gradient">
              🤖 AgentHub
            </h1>
            <p className="text-xl text-gray-300 mb-6">
              Your AI Team Orchestrator
            </p>
            <StatusBadge connected={connected} />
          </div>
        </header>

        {/* Task Input */}
        <div className="mb-8">
          <TaskInput onExecute={executeTask} isExecuting={isExecuting} />
        </div>

        {/* Agent Grid */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <span>👥</span>
            <span>AI Agents</span>
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {agents.map((agent) => (
              <AgentCard
                key={agent.name}
                agent={agent}
                isActive={activeAgent === agent.name.toLowerCase()}
              />
            ))}
          </div>
        </div>

        {/* Execution Log and Results */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Execution Log */}
          <div className="glass-strong rounded-2xl p-6 border-2 border-purple-500/20">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <span>📝</span>
              <span>Execution Log</span>
            </h2>
            <LogViewer updates={agentUpdates} />
          </div>

          {/* Results */}
          <div className="glass-strong rounded-2xl p-6 border-2 border-purple-500/20">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <span>📊</span>
              <span>Results</span>
            </h2>
            <ResultsPanel result={result} />
          </div>
        </div>

        {/* Footer */}
        <footer className="text-center mt-12 text-gray-500 text-sm">
          <p>Powered by advanced AI language models • Real-time WebSocket streaming</p>
        </footer>
      </div>
    </div>
  );
};
