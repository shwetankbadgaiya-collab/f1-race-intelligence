import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  User,
  Shield,
  CircleDot,
  MapPin,
  AlertTriangle,
  Award,
  Database,
  Info,
  Flame,
  X,
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const NAV_ITEMS = [
  { name: 'Overview', path: '/', icon: LayoutDashboard },
  { name: 'Driver Analytics', path: '/drivers', icon: User },
  { name: 'Constructor Analytics', path: '/constructors', icon: Shield },
  { name: 'Tyre Strategy', path: '/tyres', icon: CircleDot },
  { name: 'Circuit Intelligence', path: '/circuits', icon: MapPin },
  { name: 'Reliability & DNF', path: '/reliability', icon: AlertTriangle },
  { name: 'Global Podiums', path: '/podiums', icon: Award },
  { name: 'Data Explorer', path: '/data-explorer', icon: Database },
  { name: 'About Project', path: '/about', icon: Info },
];

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-[#141414] border-r border-[#262626] flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-5 border-b border-[#262626] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-1.5 h-8 bg-[#E10600] rounded-full shadow-[0_0_12px_rgba(225,6,0,0.6)]" />
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-black text-sm tracking-widest text-white uppercase">
                  F1 RACE INTELLIGENCE
                </span>
                <Flame size={14} className="text-[#E10600] inline" />
              </div>
              <p className="text-[11px] font-medium text-gray-400 tracking-wider">
                Race Analytics | 2010–2026
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-neutral-800 lg:hidden"
          >
            <X size={18} />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto custom-scrollbar">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all duration-200 ${
                    isActive
                      ? 'bg-[#E10600]/15 text-[#E10600] border-l-2 border-[#E10600] pl-3'
                      : 'text-gray-400 hover:text-white hover:bg-[#1C1C1C]'
                  }`
                }
              >
                <Icon size={16} />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Footer info & status */}
        <div className="p-4 border-t border-[#262626] bg-[#0E0E0E]">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 rounded-full bg-[#00D26A] animate-pulse" />
            <span className="text-[11px] font-medium text-gray-300">Live Telemetry Active</span>
          </div>
          <p className="text-[10px] text-gray-500 leading-tight">
            Data coverage: 2010–2024 verified. 2026 season ongoing.
          </p>
          <div className="mt-2 pt-2 border-t border-[#1F1F1F] flex items-center justify-between text-[10px] text-gray-500">
            <span>Ergast / Jolpica Core</span>
            <span className="text-[#E10600] font-mono">v1.0.0</span>
          </div>
        </div>
      </aside>
    </>
  );
}
