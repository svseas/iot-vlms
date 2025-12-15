import React from 'react';
import { Card, Statistic } from 'antd';
import type { StatisticProps } from 'antd';

interface StatsCardProps extends StatisticProps {
  onClick?: () => void;
}

const StatsCard: React.FC<StatsCardProps> = ({ onClick, ...props }) => {
  return (
    <Card
      size="small"
      hoverable={!!onClick}
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      <Statistic {...props} />
    </Card>
  );
};

export default StatsCard;
