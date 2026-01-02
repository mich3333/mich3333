import { useEffect, useRef, useState } from 'react';
import type { AgentUpdate } from '../types';
import { STATUS_COLORS } from '../types';
import { Card } from './ui/card';
import { Badge } from './ui/badge';

interface LogViewerProps {
  updates: AgentUpdate[];
}

// Agent-specific theme colors
const AGENT_THEMES = {
  manager: {
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/30',
    text: 'text-purple-400',
    icon: '🎯'
  },
  researcher: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    text: 'text-blue-400',
    icon: '🔍'
  },
  coder: {
    bg: 'bg-green-500/10',
    border: 'border-green-500/30',
    text: 'text-green-400',
    icon: '💻'
  },
  reviewer: {
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    text: 'text-amber-400',
    icon: '🔎'
  },
  reporter: {
    bg: 'bg-cyan-500/10',
    border: 'border-cyan-500/30',
    text: 'text-cyan-400',
    icon: '📊'
  },
  system: {
    bg: 'bg-text-subtle/5',
    border: 'border-border',
    text: 'text-text-subtle',
    icon: '⚙️'
  }
} as const;

export const LogViewer = ({ updates }: LogViewerProps) => {
  const logEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isUserScrolling, setIsUserScrolling] = useState<boolean>(false);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);

  // Auto-scroll with user scroll detection
  useEffect(() => {
    if (updates.length === 0) return;

    // Only auto-scroll if user hasn't manually scrolled up
    if (!isUserScrolling && logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [updates, isUserScrolling]);

  // Detect user scrolling
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isAtBottom = Math.abs(scrollHeight - clientHeight - scrollTop) < 50;

      // Mark as user scrolling if not at bottom
      setIsUserScrolling(!isAtBottom);

      // Reset after 3 seconds of no scrolling
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }

      scrollTimeoutRef.current = setTimeout(() => {
        if (isAtBottom) {
          setIsUserScrolling(false);
        }
      }, 3000);
    };

    container.addEventListener('scroll', handleScroll);
    return () => {
      container.removeEventListener('scroll', handleScroll);
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, []);

  const truncateMessage = (message: string, maxLength: number = 500) => {
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
    <div className="relative">
      <div
        ref={containerRef}
        className="space-y-3 max-h-[600px] overflow-y-auto pr-2 scroll-smooth"
        role="log"
        aria-live="polite"
        aria-atomic="false"
      >
        {updates.map((update, index) => {
          const agentKey = update.agent.toLowerCase() as keyof typeof AGENT_THEMES;
          const theme = AGENT_THEMES[agentKey] || AGENT_THEMES.system;
          const statusColor = STATUS_COLORS[update.status] || 'bg-text-subtle/10 text-text-subtle';

          return (
            <Card
              key={`${update.agent}-${index}`}
              className={`p-4 border-l-4 ${theme.border} ${theme.bg} transition-all duration-200 hover:shadow-md`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-xl" aria-hidden="true">{theme.icon}</span>
                  <span className={`font-semibold capitalize ${theme.text}`}>
                    {update.agent}
                  </span>
                </div>
                <Badge variant="outline" className={`text-xs ${statusColor}`}>
                  {update.status}
                </Badge>
              </div>

              <div className="text-sm text-text-muted leading-relaxed whitespace-pre-wrap">
                {truncateMessage(update.message)}
              </div>

              {update.timestamp && (
                <div className="text-xs text-text-subtle mt-2 flex items-center gap-1">
                  <span aria-hidden="true">🕐</span>
                  {new Date(update.timestamp).toLocaleTimeString()}
                </div>
              )}
            </Card>
          );
        })}

        {/* Scroll anchor */}
        <div ref={logEndRef} className="h-1" aria-hidden="true" />
      </div>

      {/* Scroll to bottom indicator */}
      {isUserScrolling && (
        <button
          onClick={() => {
            setIsUserScrolling(false);
            logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
          }}
          className="absolute bottom-4 right-4 bg-primary text-white px-4 py-2 rounded-full shadow-lg hover:bg-primary-hover transition-colors duration-200 flex items-center gap-2 z-10"
          aria-label="Scroll to bottom"
        >
          <span>↓</span>
          <span className="text-sm">New updates</span>
        </button>
      )}
    </div>
  );
};
