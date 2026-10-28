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

interface CircuitItem {
  circuit_id: string;
  name: string;
  country: string;
  races_hosted: number;
  dnf_rate: number;
}

interface CircuitRacesChartProps {
  data: CircuitItem[];
  limit?: number;
}

export default function CircuitRacesChart({ data, limit = 12 }: CircuitRacesChartProps) {
  const chartData = data.slice(0, limit);

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 text-xs">
        No circuit hosting statistics available.
      </div>
    );
  }

  return (
    <div className="w-full h-[340px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 10, right: 20, left: 0, bottom: 35 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
          <XAxis
            dataKey="name"
            stroke="#888"
            fontSize={10}
            tickLine={false}
            axisLine={{ stroke: '#333' }}
            interval={0}
            angle={-35}
            textAnchor="end"
          />
          <YAxis
            stroke="#666"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#333' }}
            tickFormatter={(v) => `${v}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#181818',
              borderColor: '#333',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#fff',
            }}
            formatter={(val: any, name: any, item: any) => [
              `${val} Grands Prix (DNF Rate: ${item.payload.dnf_rate}%)`,
              item.payload.country,
            ]}
          />
          <Bar dataKey="races_hosted" name="Races Hosted" radius={[4, 4, 0, 0]}>
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={index === 0 ? '#E10600' : '#3671C6'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
