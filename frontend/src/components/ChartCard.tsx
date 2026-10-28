import { motion } from 'framer-motion';
import LoadingSpinner from './LoadingSpinner';
import ErrorState from './ErrorState';
import EmptyState from './EmptyState';

interface ChartCardProps {
  title: string;
  description?: string;
  loading?: boolean;
  error?: string | null;
  isEmpty?: boolean;
  onRetry?: () => void;
  children: React.ReactNode;
  className?: string;
  action?: React.ReactNode;
}

export default function ChartCard({
  title,
  description,
  loading,
  error,
  isEmpty,
  onRetry,
  children,
  className = '',
  action,
}: ChartCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={`card p-6 ${className}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">{title}</h3>
          {description && <p className="text-xs text-gray-500 mt-1">{description}</p>}
        </div>
        {action && <div>{action}</div>}
      </div>
      <div className="min-h-[200px] flex flex-col">
        {loading ? (
          <LoadingSpinner message="Loading chart data..." />
        ) : error ? (
          <ErrorState message={error} onRetry={onRetry} />
        ) : isEmpty ? (
          <EmptyState />
        ) : (
          <div className="flex-1">{children}</div>
        )}
      </div>
    </motion.div>
  );
}
