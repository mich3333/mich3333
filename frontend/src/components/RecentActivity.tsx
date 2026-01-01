import { motion } from 'framer-motion';

interface Activity {
  id: string;
  type: 'task' | 'login' | 'logout' | 'success' | 'error';
  title: string;
  description: string;
  timestamp: string;
}

interface RecentActivityProps {
  activities: Activity[];
}

const activityConfig = {
  task: { icon: '📝', color: 'text-blue-400', bg: 'bg-blue-500/10' },
  login: { icon: '🔑', color: 'text-green-400', bg: 'bg-green-500/10' },
  logout: { icon: '🚪', color: 'text-gray-400', bg: 'bg-gray-500/10' },
  success: { icon: '✅', color: 'text-green-400', bg: 'bg-green-500/10' },
  error: { icon: '❌', color: 'text-red-400', bg: 'bg-red-500/10' },
};

export const RecentActivity = ({ activities }: RecentActivityProps) => {
  return (
    <div className="glass-strong rounded-xl p-6 border border-white/10">
      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
        <span>🕐</span>
        <span>Recent Activity</span>
      </h3>

      <div className="space-y-3 max-h-[400px] overflow-y-auto scrollbar-thin">
        {activities.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <div className="text-4xl mb-2">📭</div>
            <p>No recent activity</p>
          </div>
        ) : (
          activities.map((activity, index) => {
            const config = activityConfig[activity.type];
            return (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="glass p-3 rounded-lg border border-white/5 hover:border-purple-500/30 transition-all"
              >
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${config.bg}`}>
                    <span className="text-lg">{config.icon}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <p className="font-medium text-sm truncate">{activity.title}</p>
                      <span className="text-xs text-gray-500 whitespace-nowrap">
                        {activity.timestamp}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 line-clamp-2">{activity.description}</p>
                  </div>
                </div>
              </motion.div>
            );
          })
        )}
      </div>
    </div>
  );
};
