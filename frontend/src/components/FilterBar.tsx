import { RotateCcw, Filter, Download } from 'lucide-react';
import type { FilterState } from '../types';

interface FilterBarProps {
  filters: FilterState;
  onChange: (filters: FilterState | ((prev: FilterState) => FilterState)) => void;
  onReset: () => void;
  onExport?: () => void;
  hideDriver?: boolean;
  hideConstructor?: boolean;
  hideCircuit?: boolean;
}

const SEASONS = Array.from({ length: 15 }, (_, i) => 2024 - i); // 2024 down to 2010

export default function FilterBar({
  filters,
  onChange,
  onReset,
  onExport,
  hideDriver = false,
  hideConstructor = false,
  hideCircuit = false,
}: FilterBarProps) {
  const hasActiveFilters = Object.values(filters).some(
    (v) => v !== undefined && v !== null && v !== ''
  );

  return (
    <div className="bg-[#141414] border border-[#262626] rounded-xl p-3.5 mb-6 flex flex-wrap items-center justify-between gap-3 shadow-lg">
      <div className="flex flex-wrap items-center gap-3 flex-1">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-400 mr-1">
          <Filter size={14} className="text-[#E10600]" />
          <span>FILTERS</span>
        </div>

        {/* Season Selector */}
        <div className="flex items-center gap-2">
          <select
            value={filters.season || ''}
            onChange={(e) =>
              onChange((prev) => ({
                ...prev,
                season: e.target.value ? parseInt(e.target.value, 10) : undefined,
              }))
            }
            className="bg-[#1C1C1C] border border-[#333] hover:border-[#555] text-xs font-medium text-white rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-[#E10600] transition-colors"
          >
            <option value="">All Seasons (2010–2024)</option>
            {SEASONS.map((yr) => (
              <option key={yr} value={yr}>
                {yr} Season
              </option>
            ))}
          </select>
        </div>

        {/* Constructor Filter */}
        {!hideConstructor && (
          <select
            value={filters.constructorId || ''}
            onChange={(e) =>
              onChange((prev) => ({
                ...prev,
                constructorId: e.target.value || undefined,
              }))
            }
            className="bg-[#1C1C1C] border border-[#333] hover:border-[#555] text-xs font-medium text-white rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-[#E10600] transition-colors"
          >
            <option value="">All Constructors</option>
            <option value="red_bull">Red Bull Racing</option>
            <option value="mercedes">Mercedes</option>
            <option value="ferrari">Ferrari</option>
            <option value="mclaren">McLaren</option>
            <option value="alpine">Alpine / Renault</option>
            <option value="aston_martin">Aston Martin</option>
            <option value="williams">Williams</option>
            <option value="rb">AlphaTauri / Toro Rosso</option>
            <option value="sauber">Sauber / Alfa Romeo</option>
            <option value="haas">Haas F1 Team</option>
          </select>
        )}

        {/* Driver Filter */}
        {!hideDriver && (
          <select
            value={filters.driverId || ''}
            onChange={(e) =>
              onChange((prev) => ({
                ...prev,
                driverId: e.target.value || undefined,
              }))
            }
            className="bg-[#1C1C1C] border border-[#333] hover:border-[#555] text-xs font-medium text-white rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-[#E10600] transition-colors"
          >
            <option value="">All Drivers</option>
            <option value="max_verstappen">Max Verstappen</option>
            <option value="hamilton">Lewis Hamilton</option>
            <option value="vettel">Sebastian Vettel</option>
            <option value="alonso">Fernando Alonso</option>
            <option value="leclerc">Charles Leclerc</option>
            <option value="norris">Lando Norris</option>
            <option value="sainz">Carlos Sainz</option>
            <option value="perez">Sergio Pérez</option>
            <option value="russell">George Russell</option>
            <option value="piastri">Oscar Piastri</option>
            <option value="bottas">Valtteri Bottas</option>
            <option value="ricciardo">Daniel Ricciardo</option>
            <option value="rosberg">Nico Rosberg</option>
            <option value="raikkonen">Kimi Räikkönen</option>
          </select>
        )}

        {/* Reset Filter Button */}
        {hasActiveFilters && (
          <button
            onClick={onReset}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-gray-300 hover:text-white bg-[#222] hover:bg-[#333] transition-colors"
            title="Reset active filters"
          >
            <RotateCcw size={12} className="text-[#E10600]" />
            <span>Reset</span>
          </button>
        )}
      </div>

      {/* Export Button */}
      {onExport && (
        <button
          onClick={onExport}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-white bg-[#E10600] hover:bg-[#B30500] transition-colors shadow-sm"
        >
          <Download size={13} />
          <span>Export CSV</span>
        </button>
      )}
    </div>
  );
}
