# VLMS Technical Specification

**Project:** VMSC Lighthouse Management Software (VLMS)  
**Version:** 1.0  
**Date:** December 2025  
**Status:** Draft

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Module Specifications](#4-module-specifications)
5. [Database Design](#5-database-design)
6. [API Design](#6-api-design)
7. [IoT & Real-time Communication](#7-iot--real-time-communication)
8. [Security Requirements](#8-security-requirements)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Development Guidelines](#10-development-guidelines)

---

## 1. Executive Summary

### 1.1 Project Overview

VLMS is a comprehensive IoT-based system for remote monitoring and management of lighthouse stations. The system enables real-time monitoring of lighthouse status, energy consumption, security alerts, and predictive maintenance capabilities.

### 1.2 Key Features

| Module | Description |
|--------|-------------|
| **Real-time Dashboard** | Live monitoring of all lighthouse stations with status indicators |
| **IoT Data Pipeline** | Ingestion of sensor data via MQTT/CoAP protocols |
| **GIS Mapping** | Interactive map visualization with station clustering |
| **Alert System** | Push notifications for fire, intrusion, and equipment failures |
| **Predictive Maintenance** | ML-based failure prediction using sensor data |
| **Mobile App** | Field maintenance app with offline capabilities |
| **Reporting** | Automated Excel/PDF report generation |

### 1.3 Scale Requirements

- **Initial deployment:** 10 lighthouse stations (pilot)
- **Target scale:** 50-100 stations
- **Data ingestion rate:** ~1 message/30 seconds per station
- **Expected throughput:** ~200 messages/minute at full scale
- **Data retention:** 3 years for telemetry, 7 years for incidents

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FIELD LAYER                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │ Lighthouse  │  │ Lighthouse  │  │ Lighthouse  │  ... (n stations)        │
│  │  Station 1  │  │  Station 2  │  │  Station 3  │                          │
│  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │                          │
│  │ │IoT Gate │ │  │ │IoT Gate │ │  │ │IoT Gate │ │                          │
│  │ │ way 4G  │ │  │ │ way 4G  │ │  │ │ way 4G  │ │                          │
│  │ └────┬────┘ │  │ └────┬────┘ │  │ └────┬────┘ │                          │
│  └──────┼──────┘  └──────┼──────┘  └──────┼──────┘                          │
└─────────┼────────────────┼────────────────┼─────────────────────────────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │ MQTT/CoAP over 4G LTE
                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLOUD LAYER (GCP)                                  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        INGESTION LAYER                                │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐               │   │
│  │  │ MQTT Broker │───▶│   Redis     │───▶│   Celery    │               │   │
│  │  │  (EMQX)     │    │  (Queue)    │    │  Workers    │               │   │
│  │  └─────────────┘    └─────────────┘    └──────┬──────┘               │   │
│  └───────────────────────────────────────────────┼──────────────────────┘   │
│                                                  │                          │
│  ┌───────────────────────────────────────────────┼──────────────────────┐   │
│  │                      APPLICATION LAYER        ▼                       │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐               │   │
│  │  │  FastAPI    │◀──▶│ PostgreSQL  │◀──▶│  TimescaleDB│               │   │
│  │  │  Backend    │    │  (Primary)  │    │ (Time-series)               │   │
│  │  └──────┬──────┘    └─────────────┘    └─────────────┘               │   │
│  │         │                                                             │   │
│  │         ▼                                                             │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐               │   │
│  │  │  WebSocket  │    │   Grafana   │    │ ML Service  │               │   │
│  │  │   Server    │    │ (Monitoring)│    │ (Prediction)│               │   │
│  │  └─────────────┘    └─────────────┘    └─────────────┘               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                       STORAGE LAYER                                   │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐               │   │
│  │  │    GCS      │    │   Redis     │    │  Firebase   │               │   │
│  │  │  (Backups)  │    │  (Cache)    │    │    (FCM)    │               │   │
│  │  └─────────────┘    └─────────────┘    └─────────────┘               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                      │
│  │   React     │    │ Mobile App  │    │  Grafana    │                      │
│  │  Dashboard  │    │ (React Native)   │  Dashboard  │                      │
│  └─────────────┘    └─────────────┘    └─────────────┘                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
Sensor → IoT Gateway → MQTT Broker → Redis Queue → Celery Worker → PostgreSQL
                                          │                            │
                                          ▼                            ▼
                                     WebSocket ──────────────────▶ Dashboard
                                          │
                                          ▼
                                    Alert Service → FCM → Mobile App
```

---

## 3. Technology Stack

### 3.1 Backend: Python (FastAPI) ✅ Recommended

**Rationale for Python over Golang:**

| Criteria | Python (FastAPI) | Golang |
|----------|------------------|--------|
| **ML/AI Integration** | ✅ Native (scikit-learn, TensorFlow) | ❌ Limited, requires Python bridge |
| **Celery Integration** | ✅ Native support | ❌ Requires workarounds |
| **Development Speed** | ✅ Faster prototyping | ⚠️ More boilerplate |
| **IoT Libraries** | ✅ Excellent (paho-mqtt, asyncio) | ✅ Good |
| **Team Availability** | ✅ Easier to hire | ⚠️ Smaller talent pool |
| **Performance** | ⚠️ Good with async | ✅ Excellent |

**Verdict:** Python is recommended due to ML requirements for predictive maintenance and native Celery support. FastAPI provides near-Golang performance with async capabilities.

### 3.2 Frontend: React + Ant Design ✅ Recommended

**Recommended Stack:**

| Component | Library | Rationale |
|-----------|---------|-----------|
| **UI Framework** | **Ant Design (antd)** | Best for data-heavy admin dashboards, excellent table/form components |
| **State Management** | Zustand | Lightweight, simple API, good for medium complexity |
| **Data Fetching** | TanStack Query (React Query) | Caching, background refetch, optimistic updates |
| **Maps** | React-Leaflet + Leaflet | Free, lightweight, excellent clustering support |
| **Charts** | Recharts | React-native, composable, good performance |
| **Real-time** | Socket.io-client | Reliable WebSocket with fallbacks |
| **Forms** | React Hook Form + Zod | Type-safe validation, excellent performance |
| **Routing** | React Router v6 | Standard, nested routes support |

**Why Ant Design over alternatives:**

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| **Ant Design** | Complete component set, excellent tables, i18n support | Larger bundle | ✅ Best for admin |
| MUI (Material) | Google design, flexible | Steeper learning curve | Good alternative |
| Chakra UI | Modern, accessible | Less complete for admin | Not ideal |
| Shadcn/ui | Customizable, lightweight | Requires more setup | For custom designs |

### 3.3 Complete Technology Stack

```yaml
# Backend
backend:
  language: Python 3.11+
  framework: FastAPI
  async: uvicorn + asyncio
  validation: Pydantic v2

# Database
database:
  primary: PostgreSQL 15+
  timeseries: TimescaleDB (PostgreSQL extension)
  cache: Redis 7+
  
# Message Queue & Workers
workers:
  queue: Redis (as Celery broker)
  worker: Celery 5.x
  scheduler: Celery Beat
  
# IoT & Real-time
iot:
  mqtt_broker: EMQX (or Mosquitto)
  protocol: MQTT 3.1.1 / CoAP
  websocket: FastAPI WebSocket / Socket.io

# Monitoring & Dashboard
monitoring:
  metrics: Grafana + Prometheus
  logs: Grafana Loki
  apm: Sentry
  
# Frontend
frontend:
  framework: React 18+
  ui: Ant Design 5.x
  state: Zustand
  data: TanStack Query v5
  maps: React-Leaflet
  charts: Recharts
  forms: React Hook Form + Zod
  
# Mobile
mobile:
  framework: React Native
  navigation: React Navigation
  push: Firebase Cloud Messaging
  offline: WatermelonDB

# Infrastructure
infrastructure:
  cloud: Google Cloud Platform
  compute: Cloud Run / GKE
  database: Cloud SQL
  storage: Cloud Storage
  cdn: Cloud CDN
  ci_cd: GitHub Actions
```

---

## 4. Module Specifications

### 4.1 Backend Modules

#### 4.1.1 Core API Service

```
src/
├── api/
│   ├── v1/
│   │   ├── stations/          # Lighthouse station CRUD
│   │   ├── telemetry/         # Sensor data endpoints
│   │   ├── alerts/            # Alert management
│   │   ├── maintenance/       # Maintenance scheduling
│   │   ├── reports/           # Report generation
│   │   └── users/             # User management
│   └── deps.py                # Dependencies injection
├── core/
│   ├── config.py              # Settings management
│   ├── security.py            # Auth & permissions
│   └── exceptions.py          # Custom exceptions
├── models/                    # SQLAlchemy models
├── schemas/                   # Pydantic schemas
├── services/                  # Business logic
├── workers/                   # Celery tasks
└── main.py                    # FastAPI app
```

#### 4.1.2 Celery Workers

| Worker | Task | Priority | Retry |
|--------|------|----------|-------|
| `telemetry_processor` | Process incoming sensor data | High | 3x |
| `alert_dispatcher` | Send push notifications | Critical | 5x |
| `report_generator` | Generate Excel/PDF reports | Low | 2x |
| `ml_predictor` | Run prediction models | Medium | 1x |
| `data_aggregator` | Hourly/daily data rollups | Low | 3x |

```python
# Example Celery task
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_telemetry(self, station_id: str, payload: dict):
    """Process incoming telemetry data from IoT gateway."""
    try:
        # 1. Validate payload
        data = TelemetrySchema(**payload)
        
        # 2. Store in TimescaleDB
        store_telemetry(station_id, data)
        
        # 3. Check thresholds
        alerts = check_thresholds(station_id, data)
        
        # 4. Dispatch alerts if any
        for alert in alerts:
            dispatch_alert.delay(alert)
            
        # 5. Broadcast via WebSocket
        broadcast_update.delay(station_id, data)
        
    except Exception as e:
        self.retry(exc=e)
```

### 4.2 Frontend Modules

#### 4.2.1 Project Structure

```
src/
├── components/
│   ├── common/               # Shared components
│   ├── dashboard/            # Dashboard widgets
│   ├── map/                  # GIS components
│   ├── stations/             # Station management
│   └── reports/              # Report components
├── hooks/
│   ├── useStations.ts        # Station data hooks
│   ├── useTelemetry.ts       # Real-time telemetry
│   ├── useAlerts.ts          # Alert subscriptions
│   └── useWebSocket.ts       # WebSocket connection
├── pages/
│   ├── Dashboard/
│   ├── Stations/
│   ├── Map/
│   ├── Reports/
│   └── Settings/
├── services/
│   ├── api.ts                # API client (axios)
│   ├── websocket.ts          # Socket.io client
│   └── auth.ts               # Auth service
├── stores/
│   ├── authStore.ts          # Auth state
│   ├── stationStore.ts       # Station state
│   └── alertStore.ts         # Alert state
└── utils/
```

#### 4.2.2 Key Components

| Component | Description | Library |
|-----------|-------------|---------|
| `<StationMap />` | Interactive map with station markers | React-Leaflet |
| `<TelemetryChart />` | Real-time sensor data charts | Recharts |
| `<AlertPanel />` | Live alert notifications | Ant Design + WebSocket |
| `<StationTable />` | Station list with filters/sort | Ant Design Table |
| `<MaintenanceCalendar />` | Maintenance scheduling | Ant Design Calendar |
| `<ReportBuilder />` | Custom report generator | Custom + react-pdf |

---

## 5. Database Design

### 5.1 PostgreSQL Schema

```sql
-- Core Tables
CREATE TABLE stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    region_id UUID REFERENCES regions(id),
    status station_status DEFAULT 'active',
    commissioned_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    device_type device_type NOT NULL,
    model VARCHAR(100),
    serial_number VARCHAR(100),
    firmware_version VARCHAR(50),
    last_seen_at TIMESTAMP,
    status device_status DEFAULT 'online',
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- TimescaleDB Hypertable for Telemetry
CREATE TABLE telemetry (
    time TIMESTAMPTZ NOT NULL,
    station_id UUID NOT NULL REFERENCES stations(id),
    device_id UUID NOT NULL REFERENCES devices(id),
    metric_type VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20),
    quality INTEGER DEFAULT 100,
    metadata JSONB DEFAULT '{}'
);

SELECT create_hypertable('telemetry', 'time');

-- Continuous Aggregates for Performance
CREATE MATERIALIZED VIEW telemetry_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS bucket,
    station_id,
    metric_type,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as sample_count
FROM telemetry
GROUP BY bucket, station_id, metric_type;

-- Alerts Table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    alert_type alert_type NOT NULL,
    severity severity_level NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    acknowledged_at TIMESTAMP,
    acknowledged_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Maintenance Records
CREATE TABLE maintenance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES stations(id),
    maintenance_type maintenance_type NOT NULL,
    scheduled_at TIMESTAMP,
    completed_at TIMESTAMP,
    technician_id UUID REFERENCES users(id),
    notes TEXT,
    attachments JSONB DEFAULT '[]',
    status maintenance_status DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_telemetry_station_time ON telemetry (station_id, time DESC);
CREATE INDEX idx_alerts_station_created ON alerts (station_id, created_at DESC);
CREATE INDEX idx_stations_location ON stations USING GIST (location);
CREATE INDEX idx_stations_region ON stations (region_id);
```

### 5.2 Enums

```sql
CREATE TYPE station_status AS ENUM ('active', 'inactive', 'maintenance', 'decommissioned');
CREATE TYPE device_status AS ENUM ('online', 'offline', 'error', 'maintenance');
CREATE TYPE device_type AS ENUM ('gateway', 'sensor_power', 'sensor_security', 'camera', 'sensor_fire');
CREATE TYPE alert_type AS ENUM ('fire', 'intrusion', 'power_failure', 'device_offline', 'anomaly', 'maintenance_due');
CREATE TYPE severity_level AS ENUM ('critical', 'high', 'medium', 'low', 'info');
CREATE TYPE maintenance_type AS ENUM ('scheduled', 'corrective', 'emergency', 'inspection');
CREATE TYPE maintenance_status AS ENUM ('scheduled', 'in_progress', 'completed', 'cancelled');
```

### 5.3 Redis Data Structures

```yaml
# Real-time Station Status (Hash)
station:{station_id}:status:
  light_status: "on"
  battery_voltage: "12.6"
  solar_power: "45.2"
  last_update: "2025-12-12T10:30:00Z"
  connection_status: "online"

# Active Alerts (Sorted Set)
alerts:active:
  score: timestamp
  member: alert_id

# Station List by Region (Set)
region:{region_id}:stations:
  - station_id_1
  - station_id_2

# User Sessions (String with TTL)
session:{session_id}: user_data_json
  TTL: 86400 (24 hours)

# Rate Limiting (String with TTL)
ratelimit:{api_key}:{endpoint}: request_count
  TTL: 60 (1 minute)
```

---

## 6. API Design

### 6.1 RESTful Endpoints

#### Stations

```yaml
GET    /api/v1/stations                    # List all stations (paginated)
GET    /api/v1/stations/{id}               # Get station details
POST   /api/v1/stations                    # Create new station
PUT    /api/v1/stations/{id}               # Update station
DELETE /api/v1/stations/{id}               # Delete station
GET    /api/v1/stations/{id}/telemetry     # Get station telemetry
GET    /api/v1/stations/{id}/alerts        # Get station alerts
GET    /api/v1/stations/{id}/maintenance   # Get maintenance history
```

#### Telemetry

```yaml
GET    /api/v1/telemetry                   # Query telemetry data
POST   /api/v1/telemetry/ingest            # Ingest telemetry (internal)
GET    /api/v1/telemetry/aggregates        # Get aggregated data
GET    /api/v1/telemetry/export            # Export to CSV
```

#### Alerts

```yaml
GET    /api/v1/alerts                      # List alerts (filtered)
GET    /api/v1/alerts/{id}                 # Get alert details
POST   /api/v1/alerts/{id}/acknowledge     # Acknowledge alert
POST   /api/v1/alerts/{id}/resolve         # Resolve alert
GET    /api/v1/alerts/stats                # Alert statistics
```

#### Reports

```yaml
GET    /api/v1/reports/templates           # List report templates
POST   /api/v1/reports/generate            # Generate report
GET    /api/v1/reports/{id}/download       # Download report
GET    /api/v1/reports/scheduled           # List scheduled reports
POST   /api/v1/reports/scheduled           # Create scheduled report
```

### 6.2 WebSocket Events

```typescript
// Client → Server
interface ClientEvents {
  'subscribe:station': { stationId: string };
  'unsubscribe:station': { stationId: string };
  'subscribe:alerts': { severity?: string[] };
}

// Server → Client
interface ServerEvents {
  'telemetry:update': {
    stationId: string;
    timestamp: string;
    data: {
      lightStatus: 'on' | 'off';
      batteryVoltage: number;
      solarPower: number;
      temperature: number;
    };
  };
  'alert:new': {
    id: string;
    stationId: string;
    type: AlertType;
    severity: Severity;
    message: string;
    timestamp: string;
  };
  'station:status_change': {
    stationId: string;
    status: StationStatus;
    reason?: string;
  };
}
```

### 6.3 API Response Format

```typescript
// Success Response
interface ApiResponse<T> {
  success: true;
  data: T;
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
    hasMore?: boolean;
  };
}

// Error Response
interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
}

// Example
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "code": "LH-001",
    "name": "Đèn biển Vũng Tàu",
    "status": "active",
    "location": {
      "lat": 10.3567,
      "lng": 107.0843
    }
  }
}
```

---

## 7. IoT & Real-time Communication

### 7.1 MQTT Topic Structure

```
vlms/
├── stations/
│   └── {station_id}/
│       ├── telemetry          # Sensor data (QoS 1)
│       ├── status             # Online/offline status (QoS 1)
│       ├── alerts             # Alert triggers (QoS 2)
│       └── commands           # Remote commands (QoS 2)
├── system/
│   ├── announcements          # System-wide messages
│   └── maintenance            # Maintenance mode
└── $SYS/                      # Broker statistics
```

### 7.2 Telemetry Payload Schema

```json
{
  "station_id": "LH-001",
  "timestamp": "2025-12-12T10:30:00.000Z",
  "gateway": {
    "firmware": "2.1.0",
    "signal_strength": -67,
    "uptime_seconds": 864000
  },
  "sensors": {
    "power": {
      "battery_voltage": 12.6,
      "battery_current": -2.3,
      "solar_voltage": 18.5,
      "solar_current": 3.2,
      "load_power": 45.2
    },
    "light": {
      "status": "on",
      "intensity": 100,
      "rotation_rpm": 0.5
    },
    "security": {
      "pir_1": false,
      "pir_2": false,
      "door_sensor": "closed",
      "tamper": false
    },
    "environment": {
      "temperature": 32.5,
      "humidity": 78
    },
    "fire": {
      "smoke_detector": false,
      "heat_detector": false
    }
  }
}
```

### 7.3 Alert Triggers

```python
ALERT_THRESHOLDS = {
    "battery_voltage": {
        "critical": lambda v: v < 10.5,
        "warning": lambda v: v < 11.5,
    },
    "solar_power": {
        "warning": lambda v: v < 5 and is_daytime(),
    },
    "temperature": {
        "critical": lambda v: v > 60,
        "warning": lambda v: v > 50,
    },
    "signal_strength": {
        "warning": lambda v: v < -90,
    },
    "security_pir": {
        "critical": lambda v: v == True,  # Motion detected
    },
    "fire_smoke": {
        "critical": lambda v: v == True,  # Smoke detected
    },
}
```

---

## 8. Security Requirements

### 8.1 Authentication & Authorization

```yaml
authentication:
  method: JWT (JSON Web Tokens)
  access_token_ttl: 15 minutes
  refresh_token_ttl: 7 days
  algorithm: RS256
  
authorization:
  model: RBAC (Role-Based Access Control)
  roles:
    - super_admin    # Full system access
    - admin          # Regional management
    - operator       # View + acknowledge alerts
    - technician     # Mobile app + maintenance
    - viewer         # Read-only access
```

### 8.2 API Security

```yaml
security_headers:
  - Strict-Transport-Security: max-age=31536000
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - Content-Security-Policy: default-src 'self'
  
rate_limiting:
  authenticated: 1000 requests/minute
  unauthenticated: 100 requests/minute
  
input_validation:
  - Pydantic schema validation
  - SQL injection prevention (parameterized queries)
  - XSS prevention (output encoding)
```

### 8.3 IoT Security

```yaml
mqtt_security:
  authentication: Username/Password + Client Certificate
  encryption: TLS 1.3
  acl: Topic-level access control
  
device_security:
  firmware_signing: RSA-2048
  secure_boot: Required
  key_rotation: 90 days
```

---

## 9. Deployment Architecture

### 9.1 GCP Infrastructure

```yaml
# Compute
compute:
  api_service:
    platform: Cloud Run
    cpu: 2
    memory: 4Gi
    min_instances: 2
    max_instances: 10
    
  celery_workers:
    platform: GKE Autopilot
    replicas: 3-10 (HPA)
    cpu: 1
    memory: 2Gi
    
  mqtt_broker:
    platform: GCE (Compute Engine)
    machine: e2-medium
    disk: 50GB SSD

# Database
database:
  postgresql:
    tier: db-custom-2-8192
    storage: 100GB SSD
    ha: Regional (failover replica)
    backup: Daily, 7 days retention
    
  redis:
    tier: Standard (HA)
    memory: 4GB
    
# Storage
storage:
  backups:
    bucket: vlms-backups
    class: Nearline
    retention: 365 days
    
  reports:
    bucket: vlms-reports
    class: Standard
    cdn: Enabled
```

### 9.2 CI/CD Pipeline

```yaml
# GitHub Actions Workflow
name: Deploy VLMS

on:
  push:
    branches: [main, staging]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Tests
        run: |
          pytest --cov=src tests/
          npm run test:coverage
          
  build:
    needs: test
    steps:
      - name: Build Docker Images
        run: |
          docker build -t gcr.io/$PROJECT/vlms-api:$SHA .
          docker build -t gcr.io/$PROJECT/vlms-worker:$SHA ./worker
          
  deploy:
    needs: build
    steps:
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy vlms-api \
            --image gcr.io/$PROJECT/vlms-api:$SHA \
            --region asia-southeast1
```

### 9.3 Monitoring & Observability

```yaml
monitoring:
  metrics:
    platform: Prometheus + Grafana
    dashboards:
      - System Health
      - API Performance
      - Station Status Overview
      - Alert Analytics
      
  logging:
    platform: Grafana Loki
    retention: 30 days
    
  tracing:
    platform: OpenTelemetry + Jaeger
    sampling: 10%
    
  alerting:
    platform: Grafana Alerting
    channels:
      - Slack (#vlms-alerts)
      - Email (ops@company.com)
      - PagerDuty (critical)
```

---

## 10. Development Guidelines

### 10.1 Code Standards

```yaml
python:
  formatter: Black
  linter: Ruff
  type_checker: mypy
  docstring: Google style
  
typescript:
  formatter: Prettier
  linter: ESLint
  strict_mode: true
  
git:
  branch_naming: feature/*, bugfix/*, hotfix/*
  commit_format: Conventional Commits
  pr_template: Required
  code_review: 1 approval minimum
```

### 10.2 Testing Requirements

```yaml
coverage:
  backend: 80% minimum
  frontend: 70% minimum
  
test_types:
  unit: pytest / Jest
  integration: pytest + testcontainers
  e2e: Playwright
  load: Locust
```

### 10.3 Definition of Done

- [ ] Code reviewed and approved
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] No critical security issues
- [ ] Performance benchmarks met
- [ ] Deployed to staging
- [ ] QA sign-off

---

## Appendix A: Environment Variables

```bash
# Application
APP_ENV=production
APP_DEBUG=false
APP_SECRET_KEY=<secret>

# Database
DATABASE_URL=postgresql://user:pass@host:5432/vlms
REDIS_URL=redis://host:6379/0

# MQTT
MQTT_BROKER_URL=mqtt://host:1883
MQTT_USERNAME=vlms
MQTT_PASSWORD=<secret>

# External Services
GOOGLE_MAPS_API_KEY=<key>
FIREBASE_CREDENTIALS=<json>
SENTRY_DSN=<dsn>

# Feature Flags
FEATURE_ML_PREDICTIONS=true
FEATURE_GRAFANA_EMBED=true
```

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **VLMS** | VMSC Lighthouse Management Software |
| **Telemetry** | Sensor data transmitted from field devices |
| **Gateway** | IoT device that aggregates sensor data and transmits to cloud |
| **Hypertable** | TimescaleDB table optimized for time-series data |
| **FCM** | Firebase Cloud Messaging for push notifications |
| **HPA** | Horizontal Pod Autoscaler (Kubernetes) |

---

*Document maintained by: Engineering Team*  
*Last updated: December 2025*
