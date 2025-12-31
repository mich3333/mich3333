import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import type { AgentUpdate, ExecutionResult } from '../types';

interface UseWebSocketReturn {
  connected: boolean;
  executeTask: (task: string) => void;
  agentUpdates: AgentUpdate[];
  result: ExecutionResult | null;
  isExecuting: boolean;
}

export const useWebSocket = (serverUrl: string): UseWebSocketReturn => {
  const socketRef = useRef<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [agentUpdates, setAgentUpdates] = useState<AgentUpdate[]>([]);
  const [result, setResult] = useState<ExecutionResult | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  useEffect(() => {
    // Initialize socket connection
    socketRef.current = io(serverUrl, {
      transports: ['websocket', 'polling']
    });

    const socket = socketRef.current;

    socket.on('connect', () => {
      console.log('✅ Connected to WebSocket');
      setConnected(true);
    });

    socket.on('disconnect', () => {
      console.log('❌ Disconnected from WebSocket');
      setConnected(false);
    });

    socket.on('agent_update', (data: AgentUpdate) => {
      console.log('📡 Agent update:', data);
      setAgentUpdates(prev => [...prev, { ...data, timestamp: new Date().toISOString() }]);
    });

    socket.on('execution_complete', (data: ExecutionResult) => {
      console.log('✅ Execution complete:', data);
      setResult(data);
      setIsExecuting(false);
    });

    socket.on('error', (error: any) => {
      console.error('❌ Socket error:', error);
      setIsExecuting(false);
    });

    return () => {
      socket.disconnect();
    };
  }, [serverUrl]);

  const executeTask = useCallback((task: string) => {
    if (!socketRef.current || !connected) {
      console.error('Socket not connected');
      return;
    }

    setIsExecuting(true);
    setAgentUpdates([]);
    setResult(null);

    socketRef.current.emit('execute_realtime', { task });
  }, [connected]);

  return {
    connected,
    executeTask,
    agentUpdates,
    result,
    isExecuting
  };
};
