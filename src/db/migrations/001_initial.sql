-- VLMS Initial Database Schema
-- Version: 001
-- Description: Create initial tables for lighthouse management system

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Enums
CREATE TYPE station_status AS ENUM ('active', 'inactive', 'maintenance', 'decommissioned');
CREATE TYPE device_status AS ENUM ('online', 'offline', 'error', 'maintenance');
CREATE TYPE device_type AS ENUM ('gateway', 'sensor_power', 'sensor_security', 'camera', 'sensor_fire');
CREATE TYPE alert_type AS ENUM ('fire', 'intrusion', 'power_failure', 'device_offline', 'anomaly', 'maintenance_due');
CREATE TYPE severity_level AS ENUM ('critical', 'high', 'medium', 'low', 'info');
CREATE TYPE maintenance_type AS ENUM ('scheduled', 'corrective', 'emergency', 'inspection');
CREATE TYPE maintenance_status AS ENUM ('scheduled', 'in_progress', 'completed', 'cancelled');
CREATE TYPE user_role AS ENUM ('super_admin', 'admin', 'operator', 'technician', 'viewer');

-- Regions table
CREATE TABLE regions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    allowed_regions UUID[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stations table
CREATE TABLE stations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    region_id UUID REFERENCES regions(id) ON DELETE SET NULL,
    status station_status DEFAULT 'active',
    commissioned_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Devices table
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    device_type device_type NOT NULL,
    model VARCHAR(100),
    serial_number VARCHAR(100),
    firmware_version VARCHAR(50),
    last_seen_at TIMESTAMPTZ,
    status device_status DEFAULT 'online',
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Telemetry table (will be converted to hypertable if TimescaleDB is available)
CREATE TABLE telemetry (
    time TIMESTAMPTZ NOT NULL,
    station_id UUID NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20),
    quality INTEGER DEFAULT 100,
    metadata JSONB DEFAULT '{}'
);

-- Create hypertable for telemetry (TimescaleDB)
-- Uncomment if TimescaleDB is installed
-- SELECT create_hypertable('telemetry', 'time');

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    alert_type alert_type NOT NULL,
    severity severity_level NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by UUID REFERENCES users(id) ON DELETE SET NULL,
    resolved_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Maintenance records table
CREATE TABLE maintenance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    maintenance_type maintenance_type NOT NULL,
    scheduled_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    technician_id UUID REFERENCES users(id) ON DELETE SET NULL,
    notes TEXT,
    attachments JSONB DEFAULT '[]',
    status maintenance_status DEFAULT 'scheduled',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_telemetry_station_time ON telemetry (station_id, time DESC);
CREATE INDEX idx_telemetry_device_time ON telemetry (device_id, time DESC);
CREATE INDEX idx_telemetry_metric_type ON telemetry (metric_type, time DESC);
CREATE INDEX idx_alerts_station_created ON alerts (station_id, created_at DESC);
CREATE INDEX idx_alerts_severity ON alerts (severity, created_at DESC);
CREATE INDEX idx_alerts_unresolved ON alerts (resolved_at) WHERE resolved_at IS NULL;
CREATE INDEX idx_stations_location ON stations USING GIST (location);
CREATE INDEX idx_stations_region ON stations (region_id);
CREATE INDEX idx_stations_status ON stations (status);
CREATE INDEX idx_devices_station ON devices (station_id);
CREATE INDEX idx_devices_status ON devices (status);
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_role ON users (role);
CREATE INDEX idx_maintenance_station ON maintenance_records (station_id);
CREATE INDEX idx_maintenance_status ON maintenance_records (status);
CREATE INDEX idx_maintenance_scheduled ON maintenance_records (scheduled_at);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_regions_updated_at
    BEFORE UPDATE ON regions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stations_updated_at
    BEFORE UPDATE ON stations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_devices_updated_at
    BEFORE UPDATE ON devices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maintenance_records_updated_at
    BEFORE UPDATE ON maintenance_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
