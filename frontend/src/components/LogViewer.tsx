import { useEffect, useRef } from 'react';
import type { AgentUpdate } from '../types';
import { AGENT_CONFIG, STATUS_COLORS } from '../types';
import { Card } from './ui/card';
import { Badge } from './ui/badge';

interface LogViewerProps {
  updates: AgentUpdate[];
}

export const LogViewer = ({ updates }: LogViewerProps) => {
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [updates]);

  const truncateMessage = (message: string, maxLength: number = 300) => {
    if (message.length <= maxLength) return message;
    return message.substring(0, maxLength) + '...';
  };

  if (updates.length === 0) {
    return (
      <div className="text-center py-12 text-text-muted">
        <div className="text-4xl mb-3" aria-hidden="true">💭</div>
        <p>Execution log will appear here...</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2" role="log" aria-live="polite">
      {updates.map((update, index) => {
        const config = AGENT_CONFIG[update.agent.toLowerCase()];
        const statusColor = STATUS_COLORS[update.status] || 'bg-text-subtle/10 text-text-subtle';

        return (
          <Card
            key={index}
            className={`p-4 border-l-4 ${config.color} transition-all duration-200`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-xl" aria-hidden="true">{config.emoji}</span>
                <span className="font-semibold capitalize text-text">{update.agent}</span>
              </div>
              <Badge variant="outline" className={`text-xs ${statusColor}`}>
                {update.status}
              </Badge>
            </div>
            <div className="text-sm text-text-muted leading-relaxed">
              {truncateMessage(update.message)}
            </div>
            {update.timestamp && (
              <div className="text-xs text-text-subtle mt-2">
                {new Date(update.timestamp).toLocaleTimeString()}
              </div>
            )}
          </Card>
        );
      })}
      <div ref={logEndRef} />
    </div>
  );
};
