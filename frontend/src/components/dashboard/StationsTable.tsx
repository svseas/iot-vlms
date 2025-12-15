import React from 'react';
import { Card, Table, Tag } from 'antd';
import { useTranslation } from 'react-i18next';
import type { StationListItem, StationStatus } from '../../types';

const statusColors: Record<StationStatus, string> = {
  active: 'green',
  inactive: 'red',
  maintenance: 'orange',
  decommissioned: 'default',
};

interface StationsTableProps {
  stations: StationListItem[];
  loading?: boolean;
  onViewAll?: () => void;
  onRowClick?: (station: StationListItem) => void;
  maxRows?: number;
}

const StationsTable: React.FC<StationsTableProps> = ({
  stations,
  loading = false,
  onViewAll,
  onRowClick,
  maxRows = 6,
}) => {
  const { t } = useTranslation();

  const columns = [
    {
      title: t('stations.code'),
      dataIndex: 'code',
      key: 'code',
      width: 80,
    },
    {
      title: t('stations.name'),
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: t('stations.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: StationStatus) => (
        <Tag color={statusColors[status]}>
          {t(`stationStatus.${status}`).toUpperCase()}
        </Tag>
      ),
    },
  ];

  return (
    <Card
      title={t('dashboard.stationStatus')}
      size="small"
      extra={onViewAll && <a onClick={onViewAll}>{t('common.viewAll')}</a>}
    >
      <Table
        dataSource={stations.slice(0, maxRows)}
        columns={columns}
        rowKey="id"
        pagination={false}
        size="small"
        loading={loading}
        onRow={
          onRowClick
            ? (record) => ({
                onClick: () => onRowClick(record),
                style: { cursor: 'pointer' },
              })
            : undefined
        }
      />
    </Card>
  );
};

export default StationsTable;
