# FastAPI Metrics Monitoring System with Supabase

A comprehensive FastAPI application with built-in Prometheus metrics monitoring, Grafana dashboards, and Supabase database integration for real-time observability and persistent data storage.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Supabase Setup](#supabase-setup)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Metrics](#metrics)
- [Monitoring Setup](#monitoring-setup)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project implements a production-ready FastAPI application that provides comprehensive metrics monitoring using Prometheus and visualization through Grafana dashboards, with persistent data storage powered by Supabase. The system tracks both application-level metrics (HTTP requests, response times, error rates) and system-level metrics (CPU usage, memory consumption, process statistics) while storing all application data in a cloud-native PostgreSQL database.

The application is designed with observability as a first-class citizen, automatically collecting and exposing metrics in Prometheus format without requiring manual instrumentation of individual endpoints. All CRUD operations are backed by Supabase, providing real-time data capabilities, automatic backups, and scalable cloud infrastructure.

## Features

### Core Application Features
- **RESTful API**: Complete CRUD operations with persistent Supabase storage
- **Supabase Integration**: Cloud-native PostgreSQL with real-time capabilities
- **Health Checks**: Multiple health check endpoints including database connectivity
- **Async Processing**: Built on FastAPI's async capabilities for high performance
- **Data Validation**: Comprehensive request/response validation using Pydantic
- **Error Handling**: Structured error responses with proper HTTP status codes
- **CORS Support**: Configurable cross-origin resource sharing

### Database Features
- **Supabase Cloud**: Managed PostgreSQL with built-in APIs
- **Real-time Subscriptions**: Live data updates (extensible)
- **Row Level Security**: Fine-grained access control
- **Automatic Backups**: Point-in-time recovery
- **Scalable Storage**: Auto-scaling database infrastructure
- **SQL Editor**: Direct database access through Supabase dashboard

### Monitoring & Observability
- **Prometheus Integration**: Native metrics collection and exposition
- **System Metrics**: CPU, memory, disk, and process monitoring
- **HTTP Metrics**: Request rates, duration, size, and error tracking
- **Database Metrics**: Connection health and query performance
- **Custom Dashboards**: Pre-configured Grafana dashboards
- **Real-time Monitoring**: Live metrics with configurable collection intervals
- **Performance Tracking**: Request latency percentiles and throughput analysis

### Infrastructure & Deployment
- **Docker Support**: Complete containerization with multi-service orchestration
- **Docker Compose**: One-command deployment of the entire monitoring stack
- **Health Checks**: Container health monitoring and automatic restarts
- **Volume Persistence**: Data persistence for Prometheus and Grafana
- **Environment Configuration**: Flexible configuration through environment variables

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Prometheus    │    │     Grafana     │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   Metrics   │◄┼────┤ │  Scraping   │ │    │ │ Dashboards  │ │
│ │ Middleware  │ │    │ │   Engine    │ │    │ │             │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ API Routes  │ │    │ │   Storage   │ │    │ │ Queries &   │ │
│ │             │ │    │ │             │ │    │ │ Alerts      │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         │                                              │
         ▼                                              ▼
┌─────────────────┐                            ┌─────────────────┐
│    Supabase     │                            │      Users      │
│   PostgreSQL    │                            │   (Monitoring)  │
│                 │                            │                 │
│ ┌─────────────┐ │                            │                 │
│ │ data_items  │ │                            │                 │
│ │   Table     │ │                            │                 │
│ └─────────────┘ │                            │                 │
└─────────────────┘                            └─────────────────┘
```

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Supabase account (free tier available at [supabase.com](https://supabase.com))

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd fastapi-metrics-app

# Copy environment configuration
cp .env.example .env
```

### Step 2: Setup Supabase Database

**Option A: Use Pre-configured Database (Recommended for Testing)**
The application comes pre-configured with a demo Supabase instance. You can start immediately:

```bash
# Start all services with default configuration
./quick-start.sh
```

**Option B: Setup Your Own Supabase Project**
1. Create a Supabase account at [https://supabase.com](https://supabase.com)
2. Create a new project
3. Follow the detailed setup guide in [SUPABASE_SETUP.md](SUPABASE_SETUP.md)
4. Update your `.env` file with your credentials

### Step 3: Access Applications
- **FastAPI Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin123)

### Step 4: Test the API
```bash
# Check application health
curl http://localhost:8000/health

# Check database connectivity
curl http://localhost:8000/health/database

# Create a test data item
curl -X POST "http://localhost:8000/api/v1/data" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Item",
    "value": 42.5,
    "category": "demo",
    "metadata": {"source": "quick_start"}
  }'

# Retrieve all data items
curl "http://localhost:8000/api/v1/data"

# View metrics
curl "http://localhost:8000/metrics"
```

## Supabase Setup

### Quick Setup (5 minutes)

1. **Create Supabase Project**
   - Visit [https://supabase.com](https://supabase.com)
   - Sign up and create a new project
   - Note your project URL and API key

2. **Create Database Schema**
   - Open Supabase SQL Editor
   - Copy and run the SQL from [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

3. **Update Configuration**
   ```bash
   # Edit .env file
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-public-key
   ```

For detailed instructions, see [SUPABASE_SETUP.md](SUPABASE_SETUP.md).

## Installation

### Docker Deployment (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd fastapi-metrics-app

# Copy and configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SUPABASE_URL="your-supabase-url"
export SUPABASE_KEY="your-supabase-key"
export DEBUG=true

# Run the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SUPABASE_URL` | Supabase project URL | Pre-configured demo | Yes |
| `SUPABASE_KEY` | Supabase anon public key | Pre-configured demo | Yes |
| `SUPABASE_TABLE` | Database table name | `data_items` | No |
| `DEBUG` | Enable debug mode | `false` | No |
| `HOST` | Server host | `0.0.0.0` | No |
| `PORT` | Server port | `8000` | No |
| `METRICS_COLLECTION_INTERVAL` | Metrics collection frequency (seconds) | `5` | No |
| `CORS_ORIGINS` | Allowed CORS origins | `*` | No |

### Configuration Files

- **`.env`**: Environment variables for local development
- **`app/config.py`**: Application configuration management
- **`docker-compose.yml`**: Multi-service orchestration
- **`prometheus/prometheus.yml`**: Prometheus scraping configuration
- **`grafana/provisioning/`**: Grafana datasources and dashboards

## API Endpoints

### Root & Health Endpoints
- `GET /` - Root endpoint with application information
- `GET /health` - Basic health check
- `GET /health/detailed` - Comprehensive health check with system metrics
- `GET /health/database` - Database connectivity check
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe

### Data Management Endpoints
- `POST /api/v1/data` - Create new data item
- `GET /api/v1/data` - Retrieve all data items (with filtering & pagination)
- `GET /api/v1/data/{item_id}` - Retrieve specific data item
- `PUT /api/v1/data/{item_id}` - Update existing data item
- `DELETE /api/v1/data/{item_id}` - Delete data item
- `GET /api/v1/stats` - Get data statistics

### Utility Endpoints
- `POST /api/v1/simulate-load` - Simulate CPU load for testing
- `GET /metrics` - Prometheus metrics exposition
- `GET /metrics/summary` - Human-readable metrics summary

For detailed API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## Database Schema

### data_items Table

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `id` | UUID | Primary key | AUTO-GENERATED |
| `name` | TEXT | Item name | NOT NULL |
| `value` | DECIMAL | Numeric value | NOT NULL |
| `category` | TEXT | Item category | NOT NULL |
| `metadata` | JSONB | Additional data | DEFAULT '{}' |
| `created_at` | TIMESTAMP WITH TIME ZONE | Creation time | AUTO-GENERATED |
| `updated_at` | TIMESTAMP WITH TIME ZONE | Last update time | AUTO-UPDATED |

### Indexes
- `idx_data_items_category`: Speeds up category filtering
- `idx_data_items_created_at`: Speeds up date-based sorting

### Example Data
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Sample Item",
  "value": 42.5,
  "category": "demo",
  "metadata": {
    "source": "api",
    "priority": "high"
  },
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T10:30:00.000Z"
}
```

## Metrics

The application automatically collects and exposes comprehensive metrics in Prometheus format.

### System Metrics
- `process_cpu_seconds_total` - Total CPU time consumed
- `process_resident_memory_bytes` - Physical memory usage
- `process_virtual_memory_bytes` - Virtual memory usage
- `process_start_time_seconds` - Process start time
- `process_open_fds` - Open file descriptors
- `system_cpu_usage_percent` - System CPU usage
- `system_memory_usage_bytes` - System memory usage
- `system_disk_usage_bytes` - System disk usage

### HTTP Request Metrics
- `http_requests_total` - Total HTTP requests by method, endpoint, status
- `http_request_duration_seconds` - Request duration histogram
- `http_request_size_bytes` - Request size histogram
- `http_response_size_bytes` - Response size histogram
- `http_requests_in_progress` - Active requests gauge
- `http_requests_exceptions_total` - Exception counter

### Database Metrics
- Database connection health status
- Query performance metrics (extensible)

### Accessing Metrics
```bash
# Prometheus format
curl http://localhost:8000/metrics

# Human-readable summary
curl http://localhost:8000/metrics/summary
```

## Monitoring Setup

### Grafana Dashboards

The application includes pre-configured Grafana dashboards:

1. **FastAPI Overview Dashboard**
   - HTTP request rate and latency
   - Error rate and status code distribution
   - Active requests and throughput

2. **System Metrics Dashboard**
   - CPU and memory usage
   - Process statistics
   - System resource utilization

3. **Database Metrics Dashboard**
   - Connection health
   - Query performance (extensible)

### Accessing Grafana
1. Open http://localhost:3000
2. Login with `admin` / `admin123`
3. Navigate to "Dashboards" to view pre-configured dashboards

### Prometheus Targets
- FastAPI Application: `http://fastapi-app:8000/metrics`
- Prometheus itself: `http://localhost:9090/metrics`

## Development

### Project Structure
```
app/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── database.py            # Supabase client and operations
├── metrics/
│   ├── __init__.py
│   ├── system_metrics.py  # System-level metrics
│   └── http_metrics.py    # HTTP request metrics
├── middleware/
│   ├── __init__.py
│   └── metrics_middleware.py  # Metrics collection middleware
└── routers/
    ├── __init__.py
    ├── health.py          # Health check endpoints
    └── api.py             # Business logic endpoints
```

### Adding New Endpoints

1. **Create endpoint in appropriate router**:
   ```python
   # app/routers/api.py
   @router.get("/new-endpoint")
   async def new_endpoint():
       # Your logic here
       return {"message": "Hello World"}
   ```

2. **Metrics are automatically collected** by the metrics middleware

3. **Add database operations** using the Supabase client:
   ```python
   from app.database import db_client
   
   # Create item
   item = await db_client.create_item(data)
   
   # Get items
   items, count = await db_client.get_items()
   ```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## Deployment

### Production Deployment

For production deployment, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) which covers:

- Docker production configuration
- Kubernetes deployment
- Cloud platform deployment (AWS, GCP, Azure)
- Security considerations
- Performance tuning
- Backup and recovery

### Environment-Specific Configurations

**Development**:
```bash
DEBUG=true
METRICS_COLLECTION_INTERVAL=5
CORS_ORIGINS=*
```

**Production**:
```bash
DEBUG=false
METRICS_COLLECTION_INTERVAL=30
CORS_ORIGINS=https://yourdomain.com
```

### Scaling Considerations

1. **Application Scaling**
   - Horizontal scaling with multiple FastAPI instances
   - Load balancing with nginx or cloud load balancers
   - Database connection pooling

2. **Database Scaling**
   - Supabase automatically handles scaling
   - Consider read replicas for read-heavy workloads
   - Monitor database performance in Supabase dashboard

3. **Monitoring Scaling**
   - Prometheus federation for multi-cluster monitoring
   - Grafana high availability setup
   - Long-term metrics storage

## Troubleshooting

### Common Issues

**Database Connection Issues**:
```bash
# Check database health
curl http://localhost:8000/health/database

# Verify Supabase credentials
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Check application logs
docker-compose logs fastapi-app
```

**Metrics Not Appearing**:
```bash
# Check Prometheus targets
curl http://localhost:9090/targets

# Verify metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus configuration
docker-compose logs prometheus
```

*
(Content truncated due to size limit. Use line ranges to read in chunks)