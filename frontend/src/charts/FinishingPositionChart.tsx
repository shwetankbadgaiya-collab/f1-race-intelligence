import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  CartesianGrid,
} from 'recharts';

interface PositionData {
  position: string | number;
  count: number;
}

interface FinishingPositionChartProps {
  data: PositionData[];
}

export default function FinishingPositionChart({ data }: FinishingPositionChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-52 text-gray-500 text-xs">
        No finishing position distribution recorded.
      </div>
    );
  }

  return (
    <div className="w-full h-[260px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
          <XAxis
            dataKey="position"
            stroke="#888"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#333' }}
            tickFormatter={(v) => (v === 'DNF' ? 'DNF' : `P${v}`)}
          />
          <YAxis stroke="#666" fontSize={11} tickLine={false} axisLine={{ stroke: '#333' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#181818',
              borderColor: '#333',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#fff',
            }}
            formatter={(val: any, _: any, item: any) => [
              `${val} Races`,
              item.payload.position === 'DNF' ? 'Did Not Finish' : `Position ${item.payload.position}`,
            ]}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => {
              const pos = Number(entry.position);
              let color = '#3671C6';
              if (entry.position === 'DNF') color = '#E10600';
              else if (pos === 1) color = '#FFD700';
              else if (pos === 2) color = '#C0C0C0';
              else if (pos === 3) color = '#CD7F32';
              else if (pos <= 10) color = '#00D26A';
              return <Cell key={`cell-${index}`} fill={color} />;
            })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
