import { useState } from 'react';

interface TaskInputProps {
  onExecute: (task: string) => void;
  isExecuting: boolean;
}

export const TaskInput = ({ onExecute, isExecuting }: TaskInputProps) => {
  const [task, setTask] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (task.trim() && !isExecuting) {
      onExecute(task);
      setTask('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="glass-strong rounded-2xl p-6 border-2 border-purple-500/20">
      <label htmlFor="taskInput" className="block text-sm font-medium mb-3 text-gray-300">
        📝 What would you like the AI team to work on?
      </label>
      <div className="flex gap-3">
        <input
          id="taskInput"
          type="text"
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder="Describe your task... (e.g., 'Research quantum computing trends')"
          className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3
                   text-white placeholder-gray-500 focus:outline-none focus:ring-2
                   focus:ring-purple-500 focus:border-transparent transition-all"
          disabled={isExecuting}
        />
        <button
          type="submit"
          disabled={!task.trim() || isExecuting}
          className="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500
                   rounded-xl font-semibold text-white shadow-lg
                   hover:shadow-xl hover:scale-105 transition-all duration-300
                   disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
                   neon-glow-pink relative overflow-hidden group"
        >
          {isExecuting ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Processing...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              🚀 Execute
            </span>
          )}
        </button>
      </div>
    </form>
  );
};
