import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useWebSocket } from '../hooks/useWebSocket';
import { FloatingParticles } from '../components/FloatingParticles';
import { StatusBadge } from '../components/StatusBadge';
import { AgentCard } from '../components/AgentCard';
import { TaskInput } from '../components/TaskInput';
import { LogViewer } from '../components/LogViewer';
import { ResultsPanel } from '../components/ResultsPanel';
import { StatsCard } from '../components/StatsCard';
import { QuickActions } from '../components/QuickActions';
import { RecentActivity } from '../components/RecentActivity';
import type { Agent } from '../types';
import { useAuth } from '../contexts/AuthContext';

// Configure server URL - change this based on environment
const SERVER_URL = import.meta.env.VITE_SERVER_URL || 'http://localhost:5000';

export const Dashboard = () => {
  const { connected, executeTask, agentUpdates, result, isExecuting } = useWebSocket(SERVER_URL);
  const { user, signOut } = useAuth();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [view, setView] = useState<'overview' | 'agents'>('overview');

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

  // Mock data - will be replaced with real data from database
  const stats = {
    tasksRun: agentUpdates.length,
    tasksCompleted: agentUpdates.filter(u => u.status === 'completed').length,
    agentsActive: agents.length,
    successRate: agentUpdates.length > 0
      ? Math.round((agentUpdates.filter(u => u.status === 'completed').length / agentUpdates.length) * 100)
      : 0
  };

  const quickActions = [
    {
      id: '1',
      title: 'New Task',
      description: 'Start a new agent task',
      icon: '🚀',
      gradient: 'from-purple-500/10 to-purple-500/5',
      onClick: () => setView('agents')
    },
    {
      id: '2',
      title: 'History',
      description: 'View past executions',
      icon: '📜',
      gradient: 'from-blue-500/10 to-blue-500/5',
      onClick: () => console.log('History')
    },
    {
      id: '3',
      title: 'Settings',
      description: 'Manage preferences',
      icon: '⚙️',
      gradient: 'from-pink-500/10 to-pink-500/5',
      onClick: () => console.log('Settings')
    },
    {
      id: '4',
      title: 'Help',
      description: 'Get support',
      icon: '❓',
      gradient: 'from-green-500/10 to-green-500/5',
      onClick: () => console.log('Help')
    },
  ];

  const recentActivities = agentUpdates.slice(-5).reverse().map((update, index) => ({
    id: index.toString(),
    type: update.status === 'completed' ? 'success' as const : 'task' as const,
    title: `${update.agent} ${update.status}`,
    description: update.message.substring(0, 100),
    timestamp: update.timestamp ? new Date(update.timestamp).toLocaleTimeString() : 'Just now'
  }));

  return (
    <div className="min-h-screen relative">
      <FloatingParticles />

      <div className="relative z-10 container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-4">
              <div className="glass px-4 py-2 rounded-full border border-white/10">
                <span className="text-sm text-gray-400">👤 {user?.email}</span>
              </div>
              <StatusBadge connected={connected} />
            </div>
            <button
              onClick={handleLogout}
              className="glass px-6 py-2 rounded-full hover:border-red-500/50 border border-white/10 transition-all text-sm"
            >
              🚪 Logout
            </button>
          </div>

          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-black mb-3 bg-gradient-to-r from-purple-400 via-pink-500 to-purple-600 bg-clip-text text-transparent">
              🤖 AgentHub
            </h1>
            <p className="text-lg text-gray-300">
              Your AI Team Orchestrator
            </p>
          </div>
        </motion.header>

        {/* View Toggle */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="flex justify-center mb-8"
        >
          <div className="glass-strong rounded-full p-1 inline-flex gap-1">
            <button
              onClick={() => setView('overview')}
              className={`px-6 py-2 rounded-full transition-all ${
                view === 'overview'
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              📊 Overview
            </button>
            <button
              onClick={() => setView('agents')}
              className={`px-6 py-2 rounded-full transition-all ${
                view === 'agents'
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              🤖 Agents
            </button>
          </div>
        </motion.div>

        {view === 'overview' ? (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatsCard
                title="Tasks Run"
                value={stats.tasksRun}
                icon={<span className="text-2xl">🚀</span>}
                trend={{ value: 12, isPositive: true }}
                delay={0}
              />
              <StatsCard
                title="Completed"
                value={stats.tasksCompleted}
                icon={<span className="text-2xl">✅</span>}
                trend={{ value: 8, isPositive: true }}
                delay={0.1}
              />
              <StatsCard
                title="Active Agents"
                value={stats.agentsActive}
                icon={<span className="text-2xl">🤖</span>}
                delay={0.2}
              />
              <StatsCard
                title="Success Rate"
                value={`${stats.successRate}%`}
                icon={<span className="text-2xl">📈</span>}
                trend={{ value: 5, isPositive: true }}
                delay={0.3}
              />
            </div>

            {/* Main Content Grid */}
            <div className="grid lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <QuickActions actions={quickActions} />

                {/* Agents Preview */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="glass-strong rounded-xl p-6 border border-white/10"
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold flex items-center gap-2">
                      <span>👥</span>
                      <span>AI Agents</span>
                    </h3>
                    <button
                      onClick={() => setView('agents')}
                      className="text-sm text-purple-400 hover:text-purple-300 transition-colors"
                    >
                      View all →
                    </button>
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    {agents.slice(0, 3).map((agent) => (
                      <AgentCard
                        key={agent.name}
                        agent={agent}
                        isActive={activeAgent === agent.name.toLowerCase()}
                      />
                    ))}
                  </div>
                </motion.div>
              </div>

              {/* Sidebar */}
              <div>
                <RecentActivity activities={recentActivities} />
              </div>
            </div>
          </div>
        ) : (
          /* Agents View */
          <div className="space-y-8">
            {/* Task Input */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <TaskInput onExecute={executeTask} isExecuting={isExecuting} />
            </motion.div>

            {/* Agent Grid */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
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
            </motion.div>

            {/* Execution Log and Results */}
            <div className="grid lg:grid-cols-2 gap-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="glass-strong rounded-2xl p-6 border-2 border-purple-500/20"
              >
                <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                  <span>📝</span>
                  <span>Execution Log</span>
                </h2>
                <LogViewer updates={agentUpdates} />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="glass-strong rounded-2xl p-6 border-2 border-purple-500/20"
              >
                <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                  <span>📊</span>
                  <span>Results</span>
                </h2>
                <ResultsPanel result={result} />
              </motion.div>
            </div>
          </div>
        )}

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center mt-12 text-gray-500 text-sm"
        >
          <p>Powered by advanced AI language models • Real-time WebSocket streaming</p>
        </motion.footer>
      </div>
    </div>
  );
};
