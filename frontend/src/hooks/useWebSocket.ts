import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import type { AgentUpdate, ExecutionResult } from '../types';

type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

interface UseWebSocketReturn {
  connected: boolean;
  connectionState: ConnectionState;
  executeTask: (task: string) => void;
  agentUpdates: AgentUpdate[];
  result: ExecutionResult | null;
  isExecuting: boolean;
  error: string | null;
  reconnect: () => void;
}

export const useWebSocket = (serverUrl: string): UseWebSocketReturn => {
  const socketRef = useRef<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<ConnectionState>('connecting');
  const [agentUpdates, setAgentUpdates] = useState<AgentUpdate[]>([]);
  const [result, setResult] = useState<ExecutionResult | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const connect = useCallback(() => {
    setConnectionState('connecting');
    setError(null);

    // Initialize socket connection
    socketRef.current = io(serverUrl, {
      transports: ['websocket', 'polling']
    });

    const socket = socketRef.current;

    socket.on('connect', () => {
      console.log('✅ Connected to WebSocket');
      setConnected(true);
      setConnectionState('connected');
      setError(null);
    });

    socket.on('disconnect', () => {
      console.log('❌ Disconnected from WebSocket');
      setConnected(false);
      setConnectionState('disconnected');
    });

    socket.on('connect_error', (err) => {
      console.error('❌ Connection error:', err);
      setConnectionState('error');
      setError(err.message || 'Failed to connect to server');
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
      setError(error.message || 'An error occurred');
    });

    return socket;
  }, [serverUrl]);

  const reconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
    }
    connect();
  }, [connect]);

  useEffect(() => {
    const socket = connect();

    return () => {
      socket.disconnect();
    };
  }, [connect]);

  const executeTask = useCallback((task: string) => {
    if (!socketRef.current || !connected) {
      console.error('Socket not connected');
      setError('Not connected to server');
      return;
    }

    setIsExecuting(true);
    setAgentUpdates([]);
    setResult(null);
    setError(null);

    socketRef.current.emit('execute_realtime', { task });
  }, [connected]);

  return {
    connected,
    connectionState,
    executeTask,
    agentUpdates,
    result,
    isExecuting,
    error,
    reconnect
  };
};
