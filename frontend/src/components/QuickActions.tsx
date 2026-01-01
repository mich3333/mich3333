import { motion } from 'framer-motion';

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: string;
  onClick: () => void;
}

interface QuickActionsProps {
  actions: QuickAction[];
}

export const QuickActions = ({ actions }: QuickActionsProps) => {
  return (
    <div className="rounded-lg border border-border bg-surface p-6">
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-text">
        <span aria-hidden="true">⚡</span>
        <span>Quick Actions</span>
      </h3>

      <div className="grid grid-cols-2 gap-4">
        {actions.map((action, index) => (
          <motion.button
            key={action.id}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2, delay: index * 0.05 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={action.onClick}
            className="p-4 rounded-lg border border-border bg-bg-subtle hover:border-border-hover
                       transition-colors text-left group"
            aria-label={`${action.title}: ${action.description}`}
          >
            <div className="text-2xl mb-2" aria-hidden="true">{action.icon}</div>
            <div className="font-semibold text-sm mb-1 text-text">{action.title}</div>
            <div className="text-xs text-text-muted">{action.description}</div>
          </motion.button>
        ))}
      </div>
    </div>
  );
};
