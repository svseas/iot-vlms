import React, { useState } from 'react';
import {
  Table,
  Card,
  Button,
  Tag,
  Space,
  Typography,
  Select,
  Row,
  Col,
  Statistic,
  message,
} from 'antd';
import {
  ReloadOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { alertsApi } from '../services/alerts';
import type { AlertListItem, AlertType, SeverityLevel } from '../types';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const { Title } = Typography;

const severityColors: Record<SeverityLevel, string> = {
  critical: 'red',
  high: 'orange',
  medium: 'gold',
  low: 'blue',
  info: 'default',
};

const Alerts: React.FC = () => {
  const { t } = useTranslation();
  const [filters, setFilters] = useState<{
    severity?: SeverityLevel;
    alert_type?: AlertType;
    resolved?: boolean;
  }>({});
  const queryClient = useQueryClient();

  const alertTypeLabels: Record<AlertType, string> = {
    fire: t('alertType.fire'),
    intrusion: t('alertType.intrusion'),
    power_failure: t('alertType.power_failure'),
    device_offline: t('alertType.device_offline'),
    anomaly: t('alertType.anomaly'),
    maintenance_due: t('alertType.maintenance_due'),
  };

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['alerts', filters],
    queryFn: () => alertsApi.list({ ...filters, limit: 100 }),
  });

  const { data: statsData } = useQuery({
    queryKey: ['alertStats'],
    queryFn: () => alertsApi.getStats(),
  });

  const acknowledgeMutation = useMutation({
    mutationFn: alertsApi.acknowledge,
    onSuccess: () => {
      message.success(t('alerts.acknowledged'));
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['alertStats'] });
    },
  });

  const resolveMutation = useMutation({
    mutationFn: alertsApi.resolve,
    onSuccess: () => {
      message.success(t('alerts.resolved'));
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['alertStats'] });
    },
  });

  const stats = statsData?.data;

  const columns = [
    {
      title: t('alerts.station'),
      dataIndex: 'station_name',
      key: 'station_name',
    },
    {
      title: t('alerts.alert'),
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: t('alerts.type'),
      dataIndex: 'alert_type',
      key: 'alert_type',
      render: (type: AlertType) => alertTypeLabels[type] || type,
    },
    {
      title: t('alerts.severity'),
      dataIndex: 'severity',
      key: 'severity',
      render: (severity: SeverityLevel) => (
        <Tag color={severityColors[severity]}>{t(`alertSeverity.${severity}`).toUpperCase()}</Tag>
      ),
    },
    {
      title: t('alerts.status'),
      key: 'status',
      render: (_: unknown, record: AlertListItem) => {
        if (record.resolved_at) {
          return <Tag color="green">{t('alertStatus.resolved').toUpperCase()}</Tag>;
        }
        if (record.acknowledged_at) {
          return <Tag color="blue">{t('alertStatus.acknowledged').toUpperCase()}</Tag>;
        }
        return <Tag color="red">{t('alertStatus.pending').toUpperCase()}</Tag>;
      },
    },
    {
      title: t('alerts.time'),
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => (
        <span title={dayjs(date).format('YYYY-MM-DD HH:mm:ss')}>
          {dayjs(date).fromNow()}
        </span>
      ),
    },
    {
      title: t('common.actions'),
      key: 'actions',
      render: (_: unknown, record: AlertListItem) => (
        <Space>
          {!record.acknowledged_at && (
            <Button
              type="link"
              size="small"
              onClick={() => acknowledgeMutation.mutate(record.id)}
              loading={acknowledgeMutation.isPending}
            >
              {t('alerts.acknowledge')}
            </Button>
          )}
          {!record.resolved_at && (
            <Button
              type="link"
              size="small"
              onClick={() => resolveMutation.mutate(record.id)}
              loading={resolveMutation.isPending}
            >
              {t('alerts.resolve')}
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>
          {t('alerts.title')}
        </Title>
        <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
          {t('common.refresh')}
        </Button>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title={t('alertSeverity.critical')}
              value={stats?.critical || 0}
              valueStyle={{ color: '#ff4d4f' }}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title={t('alertSeverity.high')}
              value={stats?.high || 0}
              valueStyle={{ color: '#fa8c16' }}
              prefix={<WarningOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title={t('alerts.unacknowledged')}
              value={stats?.unacknowledged || 0}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title={t('alertStatus.resolved')}
              value={(stats?.total || 0) - (stats?.unresolved || 0)}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Select
            placeholder={t('alerts.filterBySeverity')}
            style={{ width: 180 }}
            allowClear
            onChange={(value) => setFilters((f) => ({ ...f, severity: value }))}
            options={[
              { value: 'critical', label: t('alertSeverity.critical') },
              { value: 'high', label: t('alertSeverity.high') },
              { value: 'medium', label: t('alertSeverity.medium') },
              { value: 'low', label: t('alertSeverity.low') },
              { value: 'info', label: t('alertSeverity.info') },
            ]}
          />
          <Select
            placeholder={t('alerts.filterByType')}
            style={{ width: 180 }}
            allowClear
            onChange={(value) => setFilters((f) => ({ ...f, alert_type: value }))}
            options={Object.entries(alertTypeLabels).map(([value, label]) => ({
              value,
              label,
            }))}
          />
          <Select
            placeholder={t('alerts.filterByStatus')}
            style={{ width: 180 }}
            allowClear
            onChange={(value) =>
              setFilters((f) => ({
                ...f,
                resolved: value === undefined ? undefined : value === 'resolved',
              }))
            }
            options={[
              { value: 'unresolved', label: t('alertStatus.unresolved') },
              { value: 'resolved', label: t('alertStatus.resolved') },
            ]}
          />
        </Space>

        <Table
          dataSource={data?.data || []}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          pagination={{
            total: data?.meta?.total || 0,
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => t('alerts.totalAlerts', { count: total }),
          }}
        />
      </Card>
    </div>
  );
};

export default Alerts;
