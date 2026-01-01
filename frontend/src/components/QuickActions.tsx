import { motion } from 'framer-motion';

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: string;
  gradient: string;
  onClick: () => void;
}

interface QuickActionsProps {
  actions: QuickAction[];
}

export const QuickActions = ({ actions }: QuickActionsProps) => {
  return (
    <div className="glass-strong rounded-xl p-6 border border-white/10">
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
        <span>⚡</span>
        <span>Quick Actions</span>
      </h3>

      <div className="grid grid-cols-2 gap-3">
        {actions.map((action, index) => (
          <motion.button
            key={action.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={action.onClick}
            className={`glass p-4 rounded-lg border border-white/10 hover:border-purple-500/50
                       transition-all text-left group bg-gradient-to-br ${action.gradient}`}
          >
            <div className="text-2xl mb-2">{action.icon}</div>
            <div className="font-semibold text-sm mb-1">{action.title}</div>
            <div className="text-xs text-gray-400">{action.description}</div>
          </motion.button>
        ))}
      </div>
    </div>
  );
};
