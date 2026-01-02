import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useWebSocket } from '../hooks/useWebSocket';
import { AgentCard } from '../components/AgentCard';
import { TaskInput } from '../components/TaskInput';
import { LogViewer } from '../components/LogViewer';
import { ResultsPanel } from '../components/ResultsPanel';
import { RecentActivity } from '../components/RecentActivity';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Button } from '../components/ui/button';
import type { Agent } from '../types';
import { useAuth } from '../contexts/AuthContext';

// Configure server URL - change this based on environment
const SERVER_URL = import.meta.env.VITE_SERVER_URL || 'http://localhost:5000';

export const Dashboard = () => {
  const { connectionState, executeTask, agentUpdates, result, isExecuting, error, reconnect } = useWebSocket(SERVER_URL);
  const { user, signOut } = useAuth();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [agentsLoading, setAgentsLoading] = useState(true);
  const [agentsError, setAgentsError] = useState<string | null>(null);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [showLogs, setShowLogs] = useState(false);

  const handleLogout = async () => {
    await signOut();
  };

  // Load agents on mount
  const loadAgents = async () => {
    setAgentsLoading(true);
    setAgentsError(null);
    try {
      const res = await fetch(`${SERVER_URL}/agents`);
      if (!res.ok) throw new Error('Failed to load agents');
      const data = await res.json();
      setAgents(data.agents);
    } catch (err) {
      console.error('Failed to load agents:', err);
      setAgentsError(err instanceof Error ? err.message : 'Failed to load agents');
    } finally {
      setAgentsLoading(false);
    }
  };

  useEffect(() => {
    loadAgents();
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

  // Auto-expand logs when execution starts
  useEffect(() => {
    if (isExecuting && !showLogs) {
      setShowLogs(true);
    }
  }, [isExecuting, showLogs]);

  // Stats for header
  const stats = {
    tasksRun: agentUpdates.length,
    tasksCompleted: agentUpdates.filter(u => u.status === 'completed').length,
    successRate: agentUpdates.length > 0
      ? Math.round((agentUpdates.filter(u => u.status === 'completed').length / agentUpdates.length) * 100)
      : 0
  };

  const recentActivities = agentUpdates.slice(-5).reverse().map((update, index) => ({
    id: index.toString(),
    type: update.status === 'completed' ? 'success' as const : 'task' as const,
    title: `${update.agent} ${update.status}`,
    description: update.message.substring(0, 100),
    timestamp: update.timestamp ? new Date(update.timestamp).toLocaleTimeString() : 'Just now'
  }));

  // Connection status badge variant
  const getConnectionBadgeVariant = () => {
    if (connectionState === 'connected') return 'default';
    if (connectionState === 'error') return 'error';
    return 'secondary';
  };

  const getConnectionText = () => {
    if (connectionState === 'connected') return 'Connected';
    if (connectionState === 'connecting') return 'Connecting...';
    if (connectionState === 'error') return 'Disconnected';
    return 'Disconnected';
  };

  return (
    <div className="min-h-screen bg-bg">
      {/* A1: Header Strip - Always Visible */}
      <header className="sticky top-0 z-50 border-b border-border bg-surface/95 backdrop-blur supports-[backdrop-filter]:bg-surface/60">
        <div className="max-w-6xl mx-auto px-4 md:px-6">
          {/* Top Row: Branding + User */}
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-black bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                🤖 AgentHub
              </h1>
              <Badge variant={getConnectionBadgeVariant()} className="text-xs">
                {getConnectionText()}
              </Badge>
            </div>

            <div className="flex items-center gap-4">
              <span className="text-sm text-text-muted hidden md:inline">
                {user?.email}
              </span>
              <Button
                onClick={handleLogout}
                variant="ghost"
                size="sm"
                className="text-text-muted hover:text-error"
              >
                Logout
              </Button>
            </div>
          </div>

          {/* Bottom Row: Stats Summary (compact) */}
          <div className="flex items-center gap-6 pb-4 text-sm">
            {agentsLoading ? (
              <>
                <div className="flex items-center gap-2">
                  <span className="text-text-muted">Tasks:</span>
                  <div className="h-5 w-8 bg-bg-subtle animate-pulse rounded" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-text-muted">Completed:</span>
                  <div className="h-5 w-8 bg-bg-subtle animate-pulse rounded" />
                </div>
                <div className="flex items-center gap-2 hidden sm:flex">
                  <span className="text-text-muted">Success Rate:</span>
                  <div className="h-5 w-12 bg-bg-subtle animate-pulse rounded" />
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center gap-2">
                  <span className="text-text-muted">Tasks:</span>
                  <span className="font-semibold text-text">{stats.tasksRun}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-text-muted">Completed:</span>
                  <span className="font-semibold text-success">{stats.tasksCompleted}</span>
                </div>
                <div className="flex items-center gap-2 hidden sm:flex">
                  <span className="text-text-muted">Success Rate:</span>
                  <span className="font-semibold text-text">{stats.successRate}%</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* WebSocket Error Banner */}
        {connectionState === 'error' && (
          <div className="border-t border-border">
            <div className="max-w-6xl mx-auto px-4 md:px-6 py-3">
              <Alert variant="error" className="mb-0">
                <AlertDescription className="flex items-center justify-between">
                  <span>{error || 'Failed to connect to server'}</span>
                  <Button onClick={reconnect} variant="outline" size="sm">
                    Reconnect
                  </Button>
                </AlertDescription>
              </Alert>
            </div>
          </div>
        )}
      </header>

      {/* Main Layout: Workspace + Sidebar */}
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-6">
        <div className="grid lg:grid-cols-[1fr_320px] gap-6">
          {/* A2: Main Workspace */}
          <div className="space-y-6">
            {/* Task Input (Prominent) */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
            >
              <TaskInput onExecute={executeTask} isExecuting={isExecuting} />
            </motion.div>

            {/* Results Panel */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.05 }}
            >
              <Card className="p-6">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-text">
                  <span>📊</span>
                  <span>Results</span>
                </h2>
                <ResultsPanel result={result} />
              </Card>
            </motion.div>

            {/* Execution Log (Collapsible) */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.1 }}
            >
              <Card className="overflow-hidden">
                <button
                  onClick={() => setShowLogs(!showLogs)}
                  className="w-full px-6 py-4 flex items-center justify-between hover:bg-surface-hover transition-colors duration-200"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xl">📝</span>
                    <h2 className="text-xl font-bold text-text">Execution Log</h2>
                    {agentUpdates.length > 0 && (
                      <Badge variant="secondary" className="ml-2">
                        {agentUpdates.length}
                      </Badge>
                    )}
                  </div>
                  <motion.span
                    animate={{ rotate: showLogs ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                    className="text-text-muted"
                  >
                    ▼
                  </motion.span>
                </button>

                <motion.div
                  initial={false}
                  animate={{
                    height: showLogs ? 'auto' : 0,
                    opacity: showLogs ? 1 : 0
                  }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="px-6 pb-6">
                    <LogViewer updates={agentUpdates} />
                  </div>
                </motion.div>
              </Card>
            </motion.div>
          </div>

          {/* A3: Side Column */}
          <div className="space-y-6">
            {/* Agents List (Compact) */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2 }}
            >
              <Card className="p-4">
                <h3 className="text-sm font-bold mb-4 flex items-center gap-2 text-text">
                  <span>👥</span>
                  <span>AI Agents</span>
                </h3>

                {agentsLoading ? (
                  <div className="space-y-2">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="h-16 bg-bg-subtle animate-pulse rounded-lg" />
                    ))}
                  </div>
                ) : agentsError ? (
                  <Alert variant="error" className="mb-0">
                    <AlertDescription className="text-xs">
                      <div className="flex flex-col gap-2">
                        <span>{agentsError}</span>
                        <Button onClick={loadAgents} variant="outline" size="sm" className="w-full">
                          Retry
                        </Button>
                      </div>
                    </AlertDescription>
                  </Alert>
                ) : agents.length === 0 ? (
                  <div className="text-center py-6">
                    <div className="text-3xl mb-2">🤖</div>
                    <p className="text-xs text-text-muted mb-3">No agents available</p>
                    <Button onClick={loadAgents} variant="outline" size="sm">
                      Retry
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {agents.map((agent) => (
                      <AgentCard
                        key={agent.name}
                        agent={agent}
                        isActive={activeAgent === agent.name.toLowerCase()}
                      />
                    ))}
                  </div>
                )}
              </Card>
            </motion.div>

            {/* Recent Activity (Compact) */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: 0.05 }}
            >
              <RecentActivity activities={recentActivities} isLoading={agentsLoading} />
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};
