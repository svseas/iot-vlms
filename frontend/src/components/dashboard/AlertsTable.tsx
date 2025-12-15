import React from 'react';
import { Card, Table, Tag } from 'antd';
import { useTranslation } from 'react-i18next';
import type { AlertListItem, SeverityLevel } from '../../types';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const severityColors: Record<SeverityLevel, string> = {
  critical: 'red',
  high: 'orange',
  medium: 'gold',
  low: 'blue',
  info: 'default',
};

interface AlertsTableProps {
  alerts: AlertListItem[];
  loading?: boolean;
  onViewAll?: () => void;
  maxRows?: number;
}

const AlertsTable: React.FC<AlertsTableProps> = ({
  alerts,
  loading = false,
  onViewAll,
  maxRows = 5,
}) => {
  const { t } = useTranslation();

  const columns = [
    {
      title: t('alerts.station'),
      dataIndex: 'station_name',
      key: 'station_name',
      width: 100,
      ellipsis: true,
    },
    {
      title: t('alerts.alert'),
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: t('alerts.severity'),
      dataIndex: 'severity',
      key: 'severity',
      width: 90,
      render: (severity: SeverityLevel) => (
        <Tag color={severityColors[severity]}>
          {t(`alertSeverity.${severity}`).toUpperCase()}
        </Tag>
      ),
    },
    {
      title: t('alerts.time'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 80,
      render: (date: string) => dayjs(date).fromNow(),
    },
  ];

  return (
    <Card
      title={t('dashboard.recentAlerts')}
      size="small"
      extra={onViewAll && <a onClick={onViewAll}>{t('common.viewAll')}</a>}
    >
      <Table
        dataSource={alerts.slice(0, maxRows)}
        columns={columns}
        rowKey="id"
        pagination={false}
        size="small"
        loading={loading}
        scroll={{ y: 200 }}
      />
    </Card>
  );
};

export default AlertsTable;
