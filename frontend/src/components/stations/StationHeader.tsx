import React from 'react';
import { Card, Row, Col, Typography, Tag, Descriptions, Button } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { Station, StationStatus } from '../../types';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

const statusColors: Record<StationStatus, string> = {
  active: 'green',
  inactive: 'red',
  maintenance: 'orange',
  decommissioned: 'default',
};

interface StationHeaderProps {
  station: Station;
  onBack?: () => void;
}

const StationHeader: React.FC<StationHeaderProps> = ({ station, onBack }) => {
  const { t } = useTranslation();

  return (
    <>
      {onBack && (
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={onBack}
          style={{ marginBottom: 16 }}
        >
          {t('stationDetail.backToStations')}
        </Button>
      )}
      <Card style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={3} style={{ margin: 0 }}>
              {station.name}
            </Title>
            <Text type="secondary">{station.code}</Text>
          </Col>
          <Col>
            <Tag
              color={statusColors[station.status]}
              style={{ fontSize: 14, padding: '4px 12px' }}
            >
              {t(`stationStatus.${station.status}`).toUpperCase()}
            </Tag>
          </Col>
        </Row>
        <Descriptions style={{ marginTop: 16 }} column={{ xs: 1, sm: 2, md: 3 }}>
          <Descriptions.Item label={t('stations.latitude')}>
            {station.location.lat.toFixed(6)}
          </Descriptions.Item>
          <Descriptions.Item label={t('stations.longitude')}>
            {station.location.lng.toFixed(6)}
          </Descriptions.Item>
          <Descriptions.Item label={t('stations.created')}>
            {dayjs(station.created_at).format('YYYY-MM-DD')}
          </Descriptions.Item>
          {station.metadata?.province ? (
            <Descriptions.Item label={t('stationDetail.province')}>
              {`${station.metadata.province}`}
            </Descriptions.Item>
          ) : null}
          {station.metadata?.established ? (
            <Descriptions.Item label={t('stationDetail.established')}>
              {`${station.metadata.established}`}
            </Descriptions.Item>
          ) : null}
          {station.metadata?.range_nm ? (
            <Descriptions.Item label={t('stationDetail.range')}>
              {`${station.metadata.range_nm} ${t('stationDetail.nauticalMiles')}`}
            </Descriptions.Item>
          ) : null}
        </Descriptions>
      </Card>
    </>
  );
};

export default StationHeader;
