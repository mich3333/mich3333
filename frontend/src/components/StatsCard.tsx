import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  delay?: number;
}

export const StatsCard = ({ title, value, icon, trend, delay = 0 }: StatsCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay }}
      className="rounded-lg border border-border bg-surface p-6 hover:border-border-hover transition-colors"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="p-3 bg-primary-muted rounded-lg" aria-hidden="true">
          {icon}
        </div>
        {trend && (
          <div
            className={`flex items-center gap-1 text-xs px-2 py-1 rounded-md ${
              trend.isPositive
                ? 'bg-success/20 text-success'
                : 'bg-error/20 text-error'
            }`}
            aria-label={`${trend.isPositive ? 'Increase' : 'Decrease'} of ${Math.abs(trend.value)} percent`}
          >
            <span aria-hidden="true">{trend.isPositive ? '↑' : '↓'}</span>
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>

      <div>
        <p className="text-text-muted text-sm mb-1">{title}</p>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.2, delay: delay + 0.1 }}
          className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent"
        >
          {value}
        </motion.p>
      </div>
    </motion.div>
  );
};
