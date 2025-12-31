import { useEffect, useRef } from 'react';
import type { AgentUpdate } from '../types';
import { AGENT_CONFIG, STATUS_COLORS } from '../types';

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
      <div className="text-center py-12 text-gray-400">
        <div className="text-4xl mb-3">💭</div>
        <p>Execution log will appear here...</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 max-h-[500px] overflow-y-auto scrollbar-thin pr-2">
      {updates.map((update, index) => {
        const config = AGENT_CONFIG[update.agent.toLowerCase()];
        const statusColor = STATUS_COLORS[update.status] || 'bg-gray-500/20 text-gray-300';

        return (
          <div
            key={index}
            className={`glass p-4 rounded-xl border-l-4 ${config.color} animate-slide-in-right`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-xl">{config.emoji}</span>
                <span className="font-semibold capitalize">{update.agent}</span>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full ${statusColor}`}>
                {update.status}
              </span>
            </div>
            <div className="text-sm text-gray-300 leading-relaxed">
              {truncateMessage(update.message)}
            </div>
            {update.timestamp && (
              <div className="text-xs text-gray-500 mt-2">
                {new Date(update.timestamp).toLocaleTimeString()}
              </div>
            )}
          </div>
        );
      })}
      <div ref={logEndRef} />
    </div>
  );
};
