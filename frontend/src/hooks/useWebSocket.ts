import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import type { AgentUpdate, ExecutionResult } from '../types';

type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

interface UseWebSocketReturn {
  connected: boolean;
  connectionState: ConnectionState;
  executeTask: (task: string) => void;
  cancelTask: () => void;
  agentUpdates: AgentUpdate[];
  result: ExecutionResult | null;
  isExecuting: boolean;
  error: string | null;
  reconnect: () => void;
  currentTaskId: string | null;
}

export const useWebSocket = (serverUrl: string): UseWebSocketReturn => {
  const socketRef = useRef<Socket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const [connected, setConnected] = useState<boolean>(false);
  const [connectionState, setConnectionState] = useState<ConnectionState>('connecting');
  const [agentUpdates, setAgentUpdates] = useState<AgentUpdate[]>([]);
  const [result, setResult] = useState<ExecutionResult | null>(null);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);

  // Use ref for scheduleReconnect to avoid circular dependency
  const scheduleReconnectRef = useRef<(() => void) | undefined>(undefined);

  const connect = useCallback(() => {
    setConnectionState('connecting');
    setError(null);

    // Clear any existing reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    // Initialize socket connection with robust options
    socketRef.current = io(serverUrl, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: maxReconnectAttempts,
      timeout: 10000
    });

    const socket = socketRef.current;

    // Connection events
    socket.on('connect', () => {
      console.log('✅ Connected to WebSocket');
      setConnected(true);
      setConnectionState('connected');
      setError(null);
      reconnectAttemptsRef.current = 0;
    });

    socket.on('disconnect', (reason) => {
      console.log('❌ Disconnected from WebSocket:', reason);
      setConnected(false);
      setConnectionState('disconnected');

      // Auto-reconnect logic
      if (reason === 'io server disconnect' && scheduleReconnectRef.current) {
        // Server initiated disconnect - reconnect manually
        scheduleReconnectRef.current();
      }
      // For other reasons, socket.io will auto-reconnect
    });

    socket.on('connect_error', (err) => {
      console.error('❌ Connection error:', err);
      setConnectionState('error');
      setError(err.message || 'Failed to connect to server');
      if (scheduleReconnectRef.current) {
        scheduleReconnectRef.current();
      }
    });

    // Status event
    socket.on('status', (data: { message: string }) => {
      console.log('📡 Status:', data.message);
    });

    // Agent update events (real-time thought process)
    socket.on('agent_update', (data: AgentUpdate) => {
      console.log('🤖 Agent update:', data);
      setAgentUpdates(prev => [...prev, {
        ...data,
        timestamp: data.timestamp || new Date().toISOString()
      }]);
    });

    // Execution lifecycle events
    socket.on('execution_start', (data: { task: string; message: string }) => {
      console.log('🚀 Execution started:', data);
      setIsExecuting(true);
      setAgentUpdates([]);
      setResult(null);
      setError(null);
    });

    socket.on('execution_complete', (data: { result: ExecutionResult; task_id: string; status: string; final_report: string }) => {
      console.log('✅ Execution complete:', data);
      setResult(data.result);
      setCurrentTaskId(null);
      setIsExecuting(false);
    });

    // Task cancellation
    socket.on('task_cancelled', (data: { task_id: string; message: string }) => {
      console.log('🛑 Task cancelled:', data);
      setIsExecuting(false);
      setCurrentTaskId(null);
      setError('Task cancelled by user');
    });

    // Error handling
    socket.on('error', (data: { message: string }) => {
      console.error('❌ Socket error:', data);
      setIsExecuting(false);
      setError(data.message || 'An error occurred');
    });

    return socket;
  }, [serverUrl]);

  // Define scheduleReconnect in useEffect to avoid ref mutation during render
  useEffect(() => {
    scheduleReconnectRef.current = () => {
      if (reconnectAttemptsRef.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
        console.log(`🔄 Scheduling reconnect in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);

        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current += 1;
          connect();
        }, delay);
      } else {
        console.error('❌ Max reconnection attempts reached');
        setError('Failed to reconnect after multiple attempts');
      }
    };
  }, [connect]);

  const reconnect = useCallback(() => {
    console.log('🔄 Manual reconnect triggered');
    reconnectAttemptsRef.current = 0;
    if (socketRef.current) {
      socketRef.current.disconnect();
    }
    connect();
  }, [connect]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- Connecting to WebSocket is an external system synchronization, which is the intended use of useEffect
    const socket = connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
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

    // Emit start_task event (new backend API)
    socketRef.current.emit('start_task', { task });
  }, [connected]);

  const cancelTask = useCallback(() => {
    if (!socketRef.current || !connected || !currentTaskId) {
      console.warn('Cannot cancel: not connected or no active task');
      return;
    }

    console.log('🛑 Cancelling task:', currentTaskId);
    socketRef.current.emit('cancel_task', { task_id: currentTaskId });
  }, [connected, currentTaskId]);

  return {
    connected,
    connectionState,
    executeTask,
    cancelTask,
    agentUpdates,
    result,
    isExecuting,
    error,
    reconnect,
    currentTaskId
  };
};
