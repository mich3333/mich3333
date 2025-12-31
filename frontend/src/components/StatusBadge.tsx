interface StatusBadgeProps {
  connected: boolean;
}

export const StatusBadge = ({ connected }: StatusBadgeProps) => {
  return (
    <div className="glass-strong px-6 py-3 rounded-full neon-glow inline-flex items-center gap-3">
      <div className="relative">
        {connected && (
          <span className="absolute h-3 w-3 rounded-full bg-green-400 animate-ping" />
        )}
        <span
          className={`relative block h-3 w-3 rounded-full ${
            connected ? 'bg-green-500' : 'bg-red-500'
          }`}
        />
      </div>
      <span className="font-semibold">
        {connected ? '🟢 Connected' : '🔴 Disconnected'}
      </span>
    </div>
  );
};
