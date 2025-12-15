import React from 'react';
import { Card } from 'antd';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface PieDataPoint {
  name: string;
  value: number;
  color: string;
  [key: string]: string | number;
}

interface PieChartCardProps {
  title: string;
  data: PieDataPoint[];
  height?: number;
  innerRadius?: number;
  outerRadius?: number;
  showLegend?: boolean;
}

const PieChartCard: React.FC<PieChartCardProps> = ({
  title,
  data,
  height = 250,
  innerRadius = 0,
  outerRadius = 80,
  showLegend = false,
}) => {
  return (
    <Card title={title} size="small">
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={innerRadius}
            outerRadius={outerRadius}
            paddingAngle={innerRadius > 0 ? 5 : 0}
            dataKey="value"
            label={({ name, value }) => `${name}: ${value}`}
            labelLine={false}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip />
          {showLegend && <Legend />}
        </PieChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default PieChartCard;
