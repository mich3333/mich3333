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
  result: Record<string, any>;
  final_report?: string;
  execution_time?: number;
}

export const AGENT_CONFIG: Record<string, { emoji: string; gradient: string; color: string }> = {
  manager: {
    emoji: '👔',
    gradient: 'from-amber-500 to-orange-500',
    color: 'border-orange-500/50 bg-orange-500/5'
  },
  researcher: {
    emoji: '🔍',
    gradient: 'from-blue-500 to-cyan-500',
    color: 'border-cyan-500/50 bg-cyan-500/5'
  },
  coder: {
    emoji: '💻',
    gradient: 'from-green-500 to-emerald-500',
    color: 'border-green-500/50 bg-green-500/5'
  },
  reviewer: {
    emoji: '🔎',
    gradient: 'from-purple-500 to-violet-500',
    color: 'border-purple-500/50 bg-purple-500/5'
  },
  reporter: {
    emoji: '📊',
    gradient: 'from-pink-500 to-rose-500',
    color: 'border-pink-500/50 bg-pink-500/5'
  }
};

export const STATUS_COLORS: Record<string, string> = {
  working: 'bg-yellow-500/20 text-yellow-300',
  completed: 'bg-green-500/20 text-green-300',
  error: 'bg-red-500/20 text-red-300',
  thinking: 'bg-blue-500/20 text-blue-300'
};
