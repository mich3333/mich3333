import { motion } from 'framer-motion';
import { Card } from './ui/card';

interface Activity {
  id: string;
  type: 'task' | 'login' | 'logout' | 'success' | 'error';
  title: string;
  description: string;
  timestamp: string;
}

interface RecentActivityProps {
  activities: Activity[];
  isLoading?: boolean;
}

const activityConfig = {
  task: { icon: '📝', color: 'text-primary', bg: 'bg-primary/10' },
  login: { icon: '🔑', color: 'text-success', bg: 'bg-success/10' },
  logout: { icon: '🚪', color: 'text-text-subtle', bg: 'bg-surface' },
  success: { icon: '✅', color: 'text-success', bg: 'bg-success/10' },
  error: { icon: '❌', color: 'text-error', bg: 'bg-error/10' },
};

export const RecentActivity = ({ activities, isLoading = false }: RecentActivityProps) => {
  return (
    <Card className="p-4">
      <h3 className="text-sm font-bold mb-4 flex items-center gap-2 text-text">
        <span>🕐</span>
        <span>Recent Activity</span>
      </h3>

      <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
        {isLoading ? (
          <div className="space-y-2">
            {[...Array(3)].map((_, i) => (
              <Card key={i} className="p-3">
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 bg-bg-subtle animate-pulse rounded-lg" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-bg-subtle animate-pulse rounded w-3/4" />
                    <div className="h-3 bg-bg-subtle animate-pulse rounded w-full" />
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : activities.length === 0 ? (
          <div className="text-center py-8 text-text-muted">
            <div className="text-3xl mb-2" aria-hidden="true">📭</div>
            <p className="text-sm">No recent activity</p>
          </div>
        ) : (
          activities.map((activity, index) => {
            const config = activityConfig[activity.type];
            return (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2, delay: index * 0.05 }}
              >
                <Card className="p-3 hover:border-border-hover transition-colors duration-200">
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg ${config.bg}`} aria-hidden="true">
                      <span className="text-base">{config.icon}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <p className="font-medium text-sm truncate text-text">{activity.title}</p>
                        <span className="text-xs text-text-subtle whitespace-nowrap">
                          {activity.timestamp}
                        </span>
                      </div>
                      <p className="text-xs text-text-muted line-clamp-2">{activity.description}</p>
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })
        )}
      </div>
    </Card>
  );
};
