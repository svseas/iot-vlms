// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  meta: PaginationMeta | null;
}

export interface ApiListResponse<T> {
  success: boolean;
  data: T[];
  meta: PaginationMeta;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  has_more: boolean;
}

// User types
export type UserRole = 'super_admin' | 'admin' | 'operator' | 'technician' | 'viewer';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Station types
export type StationStatus = 'active' | 'inactive' | 'maintenance' | 'decommissioned';

export interface Location {
  lat: number;
  lng: number;
}

export interface Station {
  id: string;
  code: string;
  name: string;
  location: Location;
  region_id: string | null;
  status: StationStatus;
  commissioned_at: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface StationListItem {
  id: string;
  code: string;
  name: string;
  location: Location;
  status: StationStatus;
  region_id: string | null;
  created_at: string;
}

export interface StationCreateRequest {
  code: string;
  name: string;
  location: Location;
  region_id?: string;
  metadata?: Record<string, unknown>;
}

// Alert types
export type AlertType = 'fire' | 'intrusion' | 'power_failure' | 'device_offline' | 'anomaly' | 'maintenance_due';
export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low' | 'info';

export interface Alert {
  id: string;
  station_id: string;
  station_name?: string;
  alert_type: AlertType;
  severity: SeverityLevel;
  title: string;
  message?: string;
  acknowledged_at: string | null;
  acknowledged_by: string | null;
  resolved_at: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface AlertListItem {
  id: string;
  station_id: string;
  station_name: string;
  alert_type: AlertType;
  severity: SeverityLevel;
  title: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
  created_at: string;
}

export interface AlertCreateRequest {
  station_id: string;
  alert_type: AlertType;
  severity: SeverityLevel;
  title: string;
  message?: string;
  metadata?: Record<string, unknown>;
}

export interface AlertStats {
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
  unacknowledged: number;
  unresolved: number;
}

// Telemetry types
export interface TelemetryRecord {
  time: string;
  station_id: string;
  device_id: string;
  metric_type: string;
  value: number;
  unit: string | null;
  quality: number;
}

export interface TelemetryAggregate {
  bucket: string;
  station_id: string;
  metric_type: string;
  avg_value: number;
  min_value: number;
  max_value: number;
  sample_count: number;
}

export interface LatestTelemetry {
  station_id: string;
  metrics: Record<string, number>;
  last_update: string;
}

export interface MetricItem {
  metric_type: string;
  value: number;
}

// Device types
export type DeviceStatus = 'online' | 'offline' | 'error' | 'maintenance';

export interface Device {
  id: string;
  station_id: string;
  device_type: string;
  model: string | null;
  serial_number: string | null;
  firmware_version: string | null;
  last_seen_at: string | null;
  status: DeviceStatus;
  config: Record<string, unknown>;
  created_at: string;
}

// Dashboard types
export interface DashboardStats {
  total_stations: number;
  active_stations: number;
  total_alerts: number;
  critical_alerts: number;
  devices_online: number;
  devices_offline: number;
}
