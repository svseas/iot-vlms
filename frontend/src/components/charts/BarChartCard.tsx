import React from 'react';
import { Card } from 'antd';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface BarDataPoint {
  name: string;
  value: number;
  color?: string;
}

interface BarChartCardProps {
  title: string;
  data: BarDataPoint[];
  color?: string;
  unit?: string;
  height?: number;
  layout?: 'horizontal' | 'vertical';
  colors?: string[];
}

const DEFAULT_COLORS = ['#1890ff', '#52c41a', '#faad14', '#ff4d4f', '#722ed1', '#13c2c2', '#eb2f96'];

const BarChartCard: React.FC<BarChartCardProps> = ({
  title,
  data,
  color = '#1890ff',
  unit = '',
  height = 250,
  layout = 'horizontal',
  colors = DEFAULT_COLORS,
}) => {
  const isVertical = layout === 'vertical';

  return (
    <Card title={title} size="small">
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} layout={layout}>
          <CartesianGrid strokeDasharray="3 3" />
          {isVertical ? (
            <>
              <XAxis type="number" fontSize={12} />
              <YAxis dataKey="name" type="category" width={60} fontSize={12} />
            </>
          ) : (
            <>
              <XAxis dataKey="name" fontSize={12} />
              <YAxis fontSize={12} />
            </>
          )}
          <Tooltip formatter={(value: number) => [`${value}${unit}`, 'Value']} />
          <Bar dataKey="value" fill={color} animationDuration={300}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color || colors[index % colors.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default BarChartCard;
