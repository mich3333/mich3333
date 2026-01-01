import type { Agent } from '../types';
import { AGENT_CONFIG } from '../types';
import { Card } from './ui/card';

interface AgentCardProps {
  agent: Agent;
  isActive?: boolean;
}

export const AgentCard = ({ agent, isActive }: AgentCardProps) => {
  const config = AGENT_CONFIG[agent.name.toLowerCase()];

  return (
    <Card
      className={`
        p-4 cursor-pointer group transition-all duration-200
        hover:border-border-hover hover:scale-[1.02]
        ${isActive ? 'ring-2 ring-primary scale-[1.05]' : ''}
      `}
      data-agent={agent.name.toLowerCase()}
      role="button"
      tabIndex={0}
      aria-label={`${agent.name} - ${agent.role}`}
      aria-pressed={isActive}
    >
      <div
        className="w-14 h-14 mx-auto mb-3 rounded-lg bg-primary-muted flex items-center justify-center text-2xl transition-transform duration-200 group-hover:scale-[1.05]"
        aria-hidden="true"
      >
        {config.emoji}
      </div>
      <div className="text-center">
        <div className="font-bold text-sm mb-1 text-text">{agent.name}</div>
        <div className="text-xs text-text-muted">{agent.role}</div>
      </div>
    </Card>
  );
};
