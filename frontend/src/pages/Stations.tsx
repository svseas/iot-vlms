import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table,
  Card,
  Button,
  Input,
  Tag,
  Space,
  Typography,
  Modal,
  Form,
  InputNumber,
  message,
} from 'antd';
import { PlusOutlined, SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { stationsApi } from '../services/stations';
import type { StationListItem, StationCreateRequest, StationStatus } from '../types';
import dayjs from 'dayjs';

const { Title } = Typography;

const statusColors: Record<StationStatus, string> = {
  active: 'green',
  inactive: 'red',
  maintenance: 'orange',
  decommissioned: 'default',
};

const Stations: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['stations', search],
    queryFn: () => stationsApi.list({ search: search || undefined, limit: 100 }),
  });

  const createMutation = useMutation({
    mutationFn: stationsApi.create,
    onSuccess: () => {
      message.success(t('stations.createSuccess'));
      setIsModalOpen(false);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['stations'] });
    },
    onError: () => {
      message.error(t('stations.createError'));
    },
  });

  const handleCreate = (values: { code: string; name: string; lat: number; lng: number }) => {
    const data: StationCreateRequest = {
      code: values.code,
      name: values.name,
      location: { lat: values.lat, lng: values.lng },
    };
    createMutation.mutate(data);
  };

  const columns = [
    {
      title: t('stations.code'),
      dataIndex: 'code',
      key: 'code',
      width: 100,
    },
    {
      title: t('stations.name'),
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: t('stations.status'),
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: StationStatus) => (
        <Tag color={statusColors[status]}>{t(`stationStatus.${status}`).toUpperCase()}</Tag>
      ),
    },
    {
      title: t('stations.latitude'),
      key: 'lat',
      width: 120,
      render: (_: unknown, record: StationListItem) => record.location.lat.toFixed(6),
    },
    {
      title: t('stations.longitude'),
      key: 'lng',
      width: 120,
      render: (_: unknown, record: StationListItem) => record.location.lng.toFixed(6),
    },
    {
      title: t('stations.created'),
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: t('common.actions'),
      key: 'actions',
      width: 150,
      render: (_: unknown, record: StationListItem) => (
        <Space>
          <Button type="link" size="small" onClick={() => navigate(`/stations/${record.id}`)}>
            {t('common.view')}
          </Button>
          <Button type="link" size="small">
            {t('common.edit')}
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>
          {t('stations.title')}
        </Title>
        <Space>
          <Input
            placeholder={t('stations.searchPlaceholder')}
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 250 }}
            allowClear
          />
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            {t('common.refresh')}
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
            {t('stations.addStation')}
          </Button>
        </Space>
      </div>

      <Card>
        <Table
          dataSource={data?.data || []}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          pagination={{
            total: data?.meta?.total || 0,
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => t('stations.totalStations', { count: total }),
          }}
        />
      </Card>

      <Modal
        title={t('stations.addNewStation')}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="code"
            label={t('stations.stationCode')}
            rules={[{ required: true, message: t('stations.codeRequired') }]}
          >
            <Input placeholder={t('stations.codePlaceholder')} />
          </Form.Item>
          <Form.Item
            name="name"
            label={t('stations.stationName')}
            rules={[{ required: true, message: t('stations.nameRequired') }]}
          >
            <Input placeholder={t('stations.namePlaceholder')} />
          </Form.Item>
          <Form.Item label={t('stations.location')} required>
            <Space>
              <Form.Item
                name="lat"
                noStyle
                rules={[{ required: true, message: t('common.required') }]}
              >
                <InputNumber placeholder={t('stations.latitude')} step={0.0001} style={{ width: 150 }} />
              </Form.Item>
              <Form.Item
                name="lng"
                noStyle
                rules={[{ required: true, message: t('common.required') }]}
              >
                <InputNumber placeholder={t('stations.longitude')} step={0.0001} style={{ width: 150 }} />
              </Form.Item>
            </Space>
          </Form.Item>
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setIsModalOpen(false)}>{t('common.cancel')}</Button>
              <Button type="primary" htmlType="submit" loading={createMutation.isPending}>
                {t('common.create')}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Stations;
