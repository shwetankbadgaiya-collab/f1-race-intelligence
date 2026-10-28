import { motion } from 'framer-motion';
import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  message?: string;
  icon?: React.ReactNode;
}

export default function EmptyState({
  title = 'No data available',
  message = 'Try adjusting your filters or check back later.',
  icon,
}: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center gap-4 py-16"
    >
      <div className="p-3 rounded-full bg-[#252525]">
        {icon || <Inbox size={32} className="text-gray-500" />}
      </div>
      <div className="text-center">
        <p className="text-white font-medium mb-1">{title}</p>
        <p className="text-sm text-gray-500 max-w-md">{message}</p>
      </div>
    </motion.div>
  );
}
