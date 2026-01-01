import type { ExecutionResult } from '../types';
import { Card } from './ui/card';

interface ResultsPanelProps {
  result: ExecutionResult | null;
}

export const ResultsPanel = ({ result }: ResultsPanelProps) => {
  if (!result) {
    return (
      <div className="text-center py-12 text-text-muted">
        <div className="text-4xl mb-3" aria-hidden="true">📋</div>
        <p>Results will appear here...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Task Summary */}
      <Card className="p-4 border-l-4 border-primary">
        <div className="font-semibold mb-2 flex items-center gap-2 text-text">
          <span aria-hidden="true">🎯</span>
          <span>Task</span>
        </div>
        <p className="text-text-muted text-sm">{result.task}</p>
      </Card>

      {/* Final Report */}
      {result.final_report && (
        <Card className="p-6">
          <div className="font-bold text-lg mb-4 flex items-center gap-2 text-text">
            <span aria-hidden="true">📊</span>
            <span>Final Report</span>
          </div>
          <div className="prose prose-invert max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-text-muted leading-relaxed font-sans">
              {result.final_report}
            </pre>
          </div>
        </Card>
      )}

      {/* Agent Results */}
      {Object.entries(result.result || {}).map(([agentName, agentResult]) => (
        <details
          key={agentName}
          className="rounded-lg border border-border bg-surface p-4 cursor-pointer
                   hover:border-border-hover transition-all duration-200 group"
        >
          <summary className="font-semibold capitalize flex items-center justify-between text-text">
            <span className="flex items-center gap-2">
              <span className="text-lg" aria-hidden="true">
                {agentName === 'manager' && '👔'}
                {agentName === 'researcher' && '🔍'}
                {agentName === 'coder' && '💻'}
                {agentName === 'reviewer' && '🔎'}
                {agentName === 'reporter' && '📊'}
              </span>
              <span>{agentName} Results</span>
            </span>
            <span className="text-xs text-text-subtle group-hover:text-primary transition-colors duration-200">
              Click to expand
            </span>
          </summary>
          <div className="mt-4 pt-4 border-t border-border">
            <pre className="whitespace-pre-wrap text-sm text-text-muted leading-relaxed font-mono">
              {typeof agentResult === 'string'
                ? agentResult
                : JSON.stringify(agentResult, null, 2)}
            </pre>
          </div>
        </details>
      ))}

      {/* Execution Time */}
      {result.execution_time && (
        <div className="text-center text-sm text-text-subtle">
          <span aria-hidden="true">⏱️</span> Execution time: {result.execution_time.toFixed(2)}s
        </div>
      )}
    </div>
  );
};
