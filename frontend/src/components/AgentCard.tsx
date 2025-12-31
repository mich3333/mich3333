import type { Agent } from '../types';
import { AGENT_CONFIG } from '../types';

interface AgentCardProps {
  agent: Agent;
  isActive?: boolean;
}

export const AgentCard = ({ agent, isActive }: AgentCardProps) => {
  const config = AGENT_CONFIG[agent.name.toLowerCase()];

  return (
    <div
      className={`
        glass p-4 rounded-xl border-2 border-white/10
        hover:border-cyan-500/50 transition-all duration-300
        hover:scale-105 cursor-pointer group
        ${isActive ? 'ring-2 ring-purple-500 scale-110 neon-glow' : ''}
      `}
      data-agent={agent.name.toLowerCase()}
    >
      <div
        className={`
          w-14 h-14 mx-auto mb-3 rounded-xl
          bg-gradient-to-br ${config.gradient}
          flex items-center justify-center text-2xl
          transform group-hover:scale-110 transition-transform
        `}
      >
        {config.emoji}
      </div>
      <div className="text-center">
        <div className="font-bold text-sm mb-1">{agent.name}</div>
        <div className="text-xs text-gray-400">{agent.role}</div>
      </div>
    </div>
  );
};
