import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';

interface FailureReason {
  reason: string;
  count: number;
  category: string;
}

interface FailureCategoryChartProps {
  data: FailureReason[];
}

const CATEGORY_COLORS: Record<string, string> = {
  'Engine/Power Unit': '#E10600',
  'Transmission/Gearbox': '#FF8000',
  'Collision/Accident': '#E8002D',
  'Brakes/Hydraulics': '#FFB800',
  'Electrical/Electronics': '#3671C6',
  'Suspension/Steering': '#64C4FF',
  'Other / Mechanical': '#999999',
};

export default function FailureCategoryChart({ data }: FailureCategoryChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500 text-xs">
        No failure reason statistics available.
      </div>
    );
  }

  return (
    <div className="w-full h-[320px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data.slice(0, 10)}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
        >
          <XAxis
            type="number"
            stroke="#666"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#333' }}
          />
          <YAxis
            type="category"
            dataKey="reason"
            stroke="#999"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#333' }}
            width={100}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#181818',
              borderColor: '#333',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#fff',
            }}
            formatter={(value: any, name: any, item: any) => [
              `${value} Incidents`,
              `Category: ${item.payload.category}`,
            ]}
          />
          <Bar dataKey="count" radius={[0, 4, 4, 0]}>
            {data.slice(0, 10).map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={CATEGORY_COLORS[entry.category] || '#E10600'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
