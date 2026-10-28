import { useMemo } from 'react';
import type { SeasonHeatmapEntry } from '../types';

interface SeasonHeatmapChartProps {
  data: SeasonHeatmapEntry[];
}

export default function SeasonHeatmapChart({ data }: SeasonHeatmapChartProps) {
  const { seasons, constructors, matrix } = useMemo(() => {
    const seasonSet = new Set<number>();
    const constSet = new Set<string>();
    const mat: Record<string, Record<number, number>> = {};

    data.forEach((item) => {
      seasonSet.add(item.season);
      constSet.add(item.constructorName);
      if (!mat[item.constructorName]) {
        mat[item.constructorName] = {};
      }
      mat[item.constructorName][item.season] = item.position;
    });

    return {
      seasons: Array.from(seasonSet).sort((a, b) => a - b),
      constructors: Array.from(constSet).slice(0, 10),
      matrix: mat,
    };
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-gray-500 text-xs">
        No championship standings heatmap available.
      </div>
    );
  }

  const getPosBadgeClass = (pos?: number) => {
    if (!pos) return 'bg-[#1C1C1C] text-gray-600 border border-[#2A2A2A]';
    if (pos === 1) return 'bg-[#FFD700]/20 text-[#FFD700] border border-[#FFD700]/50 font-black shadow-[0_0_8px_rgba(255,215,0,0.3)]';
    if (pos === 2) return 'bg-[#C0C0C0]/20 text-[#C0C0C0] border border-[#C0C0C0]/50 font-bold';
    if (pos === 3) return 'bg-[#CD7F32]/20 text-[#CD7F32] border border-[#CD7F32]/50 font-bold';
    if (pos <= 5) return 'bg-[#00D26A]/15 text-[#00D26A] border border-[#00D26A]/30 font-medium';
    return 'bg-[#222] text-gray-400 border border-[#333]';
  };

  return (
    <div className="w-full overflow-x-auto custom-scrollbar">
      <table className="w-full text-left text-xs border-collapse">
        <thead>
          <tr className="border-b border-[#2A2A2A]">
            <th className="py-2.5 px-3 font-semibold text-gray-400 bg-[#161616] sticky left-0 z-10 w-44">
              Constructor
            </th>
            {seasons.map((s) => (
              <th key={s} className="py-2.5 px-2 font-mono text-center text-gray-400 min-w-[46px]">
                {String(s).slice(2)}'
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-[#1F1F1F]">
          {constructors.map((c) => (
            <tr key={c} className="hover:bg-[#1A1A1A] transition-colors">
              <td className="py-2 px-3 font-medium text-white bg-[#141414] sticky left-0 z-10 truncate max-w-[170px]">
                {c}
              </td>
              {seasons.map((s) => {
                const pos = matrix[c]?.[s];
                return (
                  <td key={s} className="py-2 px-1 text-center">
                    <span
                      className={`inline-flex items-center justify-center w-7 h-7 rounded text-[11px] ${getPosBadgeClass(
                        pos
                      )}`}
                    >
                      {pos ? `P${pos}` : '-'}
                    </span>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
