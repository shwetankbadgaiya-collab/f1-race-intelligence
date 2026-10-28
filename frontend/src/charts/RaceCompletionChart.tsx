import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts';

interface RaceCompletionChartProps {
  classified: number;
  dnf: number;
  dsq?: number;
}

export default function RaceCompletionChart({
  classified,
  dnf,
  dsq = 0,
}: RaceCompletionChartProps) {
  const total = classified + dnf + dsq;

  const data = [
    { name: 'Classified Finishes', value: classified, color: '#00D26A' },
    { name: 'Retirements (DNF)', value: dnf, color: '#E10600' },
    ...(dsq > 0 ? [{ name: 'Disqualifications', value: dsq, color: '#FFB800' }] : []),
  ];

  if (total === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 text-xs">
        No completion telemetry data available.
      </div>
    );
  }

  const completionRate = ((classified / total) * 100).toFixed(1);

  return (
    <div className="w-full flex flex-col items-center">
      <div className="h-[280px] w-full relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              innerRadius={70}
              outerRadius={95}
              paddingAngle={4}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} stroke="#141414" strokeWidth={2} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#181818',
                borderColor: '#333',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#fff',
              }}
              formatter={(val: any) => [`${val} (${((Number(val) / total) * 100).toFixed(1)}%)`]}
            />
            <Legend
              verticalAlign="bottom"
              wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
              formatter={(val) => <span className="text-gray-300">{val}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
        {/* Center Completion Metric */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none pb-8">
          <span className="text-2xl font-black text-white">{completionRate}%</span>
          <span className="text-[10px] text-gray-400 font-medium uppercase tracking-wider">
            Completion Rate
          </span>
        </div>
      </div>
    </div>
  );
}
