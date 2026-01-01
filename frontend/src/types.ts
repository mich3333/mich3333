export interface Agent {
  name: string;
  role: string;
  emoji: string;
}

export interface AgentUpdate {
  agent: string;
  status: 'working' | 'completed' | 'error' | 'thinking';
  message: string;
  timestamp?: string;
}

export interface ExecutionResult {
  task: string;
  result: Record<string, unknown>;
  final_report?: string;
  execution_time?: number;
}

export const AGENT_CONFIG: Record<string, { emoji: string; gradient: string; color: string }> = {
  manager: {
    emoji: '👔',
    gradient: 'from-accent to-accent',
    color: 'border-accent bg-accent/5'
  },
  researcher: {
    emoji: '🔍',
    gradient: 'from-primary to-primary',
    color: 'border-primary bg-primary/5'
  },
  coder: {
    emoji: '💻',
    gradient: 'from-success to-success',
    color: 'border-success bg-success/5'
  },
  reviewer: {
    emoji: '🔎',
    gradient: 'from-primary to-primary',
    color: 'border-primary bg-primary/5'
  },
  reporter: {
    emoji: '📊',
    gradient: 'from-accent to-accent',
    color: 'border-accent bg-accent/5'
  }
};

export const STATUS_COLORS: Record<string, string> = {
  working: 'bg-warning/10 text-warning',
  completed: 'bg-success/10 text-success',
  error: 'bg-error/10 text-error',
  thinking: 'bg-primary/10 text-primary'
};
