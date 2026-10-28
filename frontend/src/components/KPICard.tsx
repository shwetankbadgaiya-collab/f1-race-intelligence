import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';

interface KPICardProps {
  icon: LucideIcon;
  value: string | number;
  label: string;
  description?: string;
  color?: string;
  index?: number;
}

export default function KPICard({ icon: Icon, value, label, description, color = '#E10600', index = 0 }: KPICardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
      className="card-hover p-5 flex flex-col gap-3"
    >
      <div className="flex items-center justify-between">
        <div className="p-2 rounded-lg" style={{ backgroundColor: `${color}15` }}>
          <Icon size={20} style={{ color }} />
        </div>
      </div>
      <div>
        <p className="text-2xl font-bold text-white tracking-tight">{value}</p>
        <p className="text-sm font-medium text-gray-400 mt-0.5">{label}</p>
        {description && <p className="text-xs text-gray-500 mt-1">{description}</p>}
      </div>
    </motion.div>
  );
}
