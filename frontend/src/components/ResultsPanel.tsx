import type { ExecutionResult } from '../types';

interface ResultsPanelProps {
  result: ExecutionResult | null;
}

export const ResultsPanel = ({ result }: ResultsPanelProps) => {
  if (!result) {
    return (
      <div className="text-center py-12 text-gray-400">
        <div className="text-4xl mb-3">📋</div>
        <p>Results will appear here...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Task Summary */}
      <div className="glass-strong p-4 rounded-xl border-l-4 border-purple-500">
        <div className="font-semibold mb-2 flex items-center gap-2">
          <span>🎯</span>
          <span>Task</span>
        </div>
        <p className="text-gray-300 text-sm">{result.task}</p>
      </div>

      {/* Final Report */}
      {result.final_report && (
        <div className="glass-strong p-6 rounded-xl">
          <div className="font-bold text-lg mb-4 flex items-center gap-2">
            <span>📊</span>
            <span>Final Report</span>
          </div>
          <div className="prose prose-invert max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-gray-300 leading-relaxed font-sans">
              {result.final_report}
            </pre>
          </div>
        </div>
      )}

      {/* Agent Results */}
      {Object.entries(result.result || {}).map(([agentName, agentResult]) => (
        <details
          key={agentName}
          className="glass p-4 rounded-xl border border-white/10 cursor-pointer
                   hover:border-purple-500/30 transition-all group"
        >
          <summary className="font-semibold capitalize flex items-center justify-between">
            <span className="flex items-center gap-2">
              <span className="text-lg">
                {agentName === 'manager' && '👔'}
                {agentName === 'researcher' && '🔍'}
                {agentName === 'coder' && '💻'}
                {agentName === 'reviewer' && '🔎'}
                {agentName === 'reporter' && '📊'}
              </span>
              <span>{agentName} Results</span>
            </span>
            <span className="text-xs text-gray-500 group-hover:text-purple-400 transition-colors">
              Click to expand
            </span>
          </summary>
          <div className="mt-4 pt-4 border-t border-white/10">
            <pre className="whitespace-pre-wrap text-sm text-gray-400 leading-relaxed font-mono">
              {typeof agentResult === 'string'
                ? agentResult
                : JSON.stringify(agentResult, null, 2)}
            </pre>
          </div>
        </details>
      ))}

      {/* Execution Time */}
      {result.execution_time && (
        <div className="text-center text-sm text-gray-500">
          ⏱️ Execution time: {result.execution_time.toFixed(2)}s
        </div>
      )}
    </div>
  );
};
