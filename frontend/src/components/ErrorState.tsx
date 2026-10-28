import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export default function ErrorState({ message = 'Failed to load data', onRetry }: ErrorStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center gap-4 py-16"
    >
      <div className="p-3 rounded-full bg-red-500/10">
        <AlertTriangle size={32} className="text-red-400" />
      </div>
      <div className="text-center">
        <p className="text-white font-medium mb-1">Something went wrong</p>
        <p className="text-sm text-gray-400 max-w-md">{message}</p>
      </div>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary text-sm">
          <RefreshCw size={14} />
          Try Again
        </button>
      )}
    </motion.div>
  );
}
