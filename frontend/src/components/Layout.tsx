import { useState } from 'react';
import { Menu } from 'lucide-react';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white flex">
      {/* Desktop & Mobile Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Area */}
      <div className="flex-1 lg:pl-64 flex flex-col min-w-0">
        {/* Mobile Top Navbar */}
        <header className="lg:hidden h-14 border-b border-[#262626] bg-[#141414] px-4 flex items-center justify-between sticky top-0 z-30">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-neutral-800"
              aria-label="Open Navigation Menu"
            >
              <Menu size={20} />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-5 bg-[#E10600] rounded-full" />
              <span className="font-bold text-xs tracking-wider uppercase text-white">
                F1 RACE INTELLIGENCE
              </span>
            </div>
          </div>
          <span className="text-[10px] text-gray-500 font-mono">2010–2026</span>
        </header>

        {/* Page Content Viewport */}
        <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-[1600px] w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
