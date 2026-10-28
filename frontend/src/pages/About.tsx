import {
  Info,
  Shield,
  Cpu,
  Database,
  Target,
  Users,
  AlertTriangle,
  Lightbulb,
  ExternalLink,
} from 'lucide-react';

export default function About() {
  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="border-b border-[#222] pb-5">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded bg-[#E10600]/20 text-[#E10600] text-xs font-mono font-bold tracking-wider uppercase">
            HACKATHON ARCHITECTURE & METHODOLOGY
          </span>
        </div>
        <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
          ABOUT F1 RACE INTELLIGENCE
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          A high-performance motorsport telemetry, championship trend analytics, and reliability research platform covering 2010 through 2026.
        </p>
      </div>

      {/* Problem Statement & Objectives */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#141414] border border-[#262626] rounded-xl p-6 space-y-3">
          <div className="flex items-center gap-2.5 text-[#E10600]">
            <Target size={20} />
            <h3 className="text-base font-bold text-white">Problem Statement</h3>
          </div>
          <p className="text-xs text-gray-300 leading-relaxed">
            Modern Formula 1 produces hundreds of gigabytes of timing transponder logs, race telemetry, and championship statistics every weekend. Broadcast viewers, data science students, journalists, and technical analysts struggle to explore historical patterns across modern hybrid eras (2010–2026) due to fragmented databases, lack of normalized schemas, and misleading simulations that fabricate historical race results.
          </p>
        </div>

        <div className="bg-[#141414] border border-[#262626] rounded-xl p-6 space-y-3">
          <div className="flex items-center gap-2.5 text-[#3671C6]">
            <Lightbulb size={20} />
            <h3 className="text-base font-bold text-white">Project Objective</h3>
          </div>
          <p className="text-xs text-gray-300 leading-relaxed">
            Build a deterministic, fully responsive, production-quality analytics platform that transforms raw race results into meaningful insights. Enable deep multi-team comparisons, driver head-to-head metrics, circuit failure rates, and reliable telemetry exploration while maintaining strict data integrity and zero fabrication of unrecorded statistics.
          </p>
        </div>
      </div>

      {/* Target Users */}
      <div className="bg-[#141414] border border-[#262626] rounded-xl p-6">
        <div className="flex items-center gap-2 text-[#00D26A] mb-4">
          <Users size={20} />
          <h3 className="text-base font-bold text-white">Target Audiences</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          {[
            {
              role: 'F1 Team Performance Strategists',
              desc: 'Macro benchmarks across historical circuit retirement patterns and competitor trajectories.',
            },
            {
              role: 'Motorsport Broadcast Analysts',
              desc: 'Rapid retrieval of driver podium conversion rates, delta comparisons, and historical context.',
            },
            {
              role: 'FIA Technical Regulation Analysts',
              desc: 'Descriptive analytics tracking engine and gearbox failure rates across regulatory eras.',
            },
            {
              role: 'Motorsport Journalists & Media',
              desc: 'Accurate, citation-ready statistics with documented denominators and era-specific points.',
            },
            {
              role: 'Formula 1 Enthusiasts',
              desc: 'Rich, interactive dark-themed telemetry visualizer with driver vs driver toolsets.',
            },
            {
              role: 'Data Science Researchers',
              desc: 'Clean, normalized SQLite/PostgreSQL schemas with CSV export and data-quality audits.',
            },
          ].map((u, idx) => (
            <div key={idx} className="p-3.5 rounded-lg bg-[#181818] border border-[#222]">
              <h4 className="font-bold text-white mb-1">{u.role}</h4>
              <p className="text-gray-400 text-[11px] leading-relaxed">{u.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Technical Architecture */}
      <div className="bg-[#141414] border border-[#262626] rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-2 text-[#FF8000]">
          <Cpu size={20} />
          <h3 className="text-base font-bold text-white">Technical Architecture</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-4 rounded-lg bg-[#181818] border border-[#262626] space-y-2">
            <span className="text-[#E10600] font-bold block text-sm">Frontend Layer</span>
            <p className="text-gray-300 font-sans text-xs">
              React 18, Vite, TypeScript, Tailwind CSS, Recharts for dynamic responsive charts, Framer Motion for micro-interactions, Lucide icons.
            </p>
          </div>
          <div className="p-4 rounded-lg bg-[#181818] border border-[#262626] space-y-2">
            <span className="text-[#3671C6] font-bold block text-sm">Backend API</span>
            <p className="text-gray-300 font-sans text-xs">
              Python 3.13, FastAPI for high-performance async REST endpoints, Pydantic v2 for request/response validation, Pandas & NumPy for aggregations.
            </p>
          </div>
          <div className="p-4 rounded-lg bg-[#181818] border border-[#262626] space-y-2">
            <span className="text-[#00D26A] font-bold block text-sm">Database & Pipeline</span>
            <p className="text-gray-300 font-sans text-xs">
              PostgreSQL-ready SQLite database, SQLAlchemy 2.0 ORM, modular Jolpica-F1 API adapter, CSV ingestion engine with integrity validation.
            </p>
          </div>
        </div>
      </div>

      {/* Data Sources & Methodology */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#141414] border border-[#262626] rounded-xl p-6 space-y-3">
          <div className="flex items-center gap-2 text-[#229971]">
            <Database size={20} />
            <h3 className="text-base font-bold text-white">Data Sources & Attribution</h3>
          </div>
          <p className="text-xs text-gray-300 leading-relaxed">
            Data is ingested from the open-source Ergast Motor Racing Database and its modern successor, the Jolpica-F1 API (<a href="https://api.jolpi.ca" target="_blank" rel="noreferrer" className="text-[#3671C6] underline">api.jolpi.ca</a>). Historical seasons 2010 through 2024 have been loaded and verified across 15 seasons, 34 circuits, 22 constructors, 43 drivers, and 5,945 race results.
          </p>
        </div>

        <div className="bg-[#141414] border border-[#262626] rounded-xl p-6 space-y-3">
          <div className="flex items-center gap-2 text-[#FFB800]">
            <Shield size={20} />
            <h3 className="text-base font-bold text-white">Analytical Methodology</h3>
          </div>
          <p className="text-xs text-gray-300 leading-relaxed">
            Championship points follow the official FIA regulations for each specific era (25-18-15-12-10-8-6-4-2-1 plus fastest lap bonus points from 2019 onward). Podium finishes are strictly defined as classified 1st, 2nd, and 3rd place finishes. DNFs represent non-classified race retirements.
          </p>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="p-4 rounded-xl bg-[#1A1408] border border-[#FFB800]/30 text-xs text-gray-300 flex items-start gap-3">
        <AlertTriangle size={18} className="text-[#FFB800] shrink-0 mt-0.5" />
        <p>
          <strong>DISCLAIMER:</strong> This dashboard is an educational research and analytics project built for hackathon evaluation. It supports human exploratory decision-making and descriptive analytics. It does not replace real-time pit wall engineering or technical regulatory investigation.
        </p>
      </div>
    </div>
  );
}
