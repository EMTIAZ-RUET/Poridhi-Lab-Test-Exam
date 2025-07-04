# FastAPI Metrics Monitoring System - API Documentation

## Overview

This document provides comprehensive documentation for all REST API endpoints available in the FastAPI Metrics Monitoring System. The API follows RESTful principles and provides JSON responses for all endpoints except the metrics endpoint which returns Prometheus format.

## Base URL

- **Local Development**: `http://localhost:8000`
- **Docker Compose**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

Currently, the API does not require authentication. In production environments, consider implementing:
- API key authentication
- JWT token-based authentication
- OAuth 2.0 integration

## Content Types

- **Request Content-Type**: `application/json`
- **Response Content-Type**: `application/json` (except `/metrics` endpoint)
- **Metrics Content-Type**: `text/plain; version=0.0.4; charset=utf-8`

## Error Handling

All endpoints return structured error responses with appropriate HTTP status codes:

### Standard Error Response Format

```json
{
  "detail": "Error description"
}
```

### Validation Error Response Format

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error message",
      "type": "error_type",
      "ctx": {"additional": "context"}
    }
  ]
}
```

## API Endpoints

### Root Endpoints

#### GET /

**Description**: Root endpoint providing application information and navigation links.

**Parameters**: None

**Response**:
```json
{
  "message": "Welcome to FastAPI Metrics Monitoring System",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health",
  "metrics": "/metrics",
  "api": "/api/v1"
}
```

**Status Codes**:
- `200 OK`: Success

**Example**:
```bash
curl -X GET "http://localhost:8000/"
```

### Health Check Endpoints

#### GET /health

**Description**: Basic health check endpoint for monitoring application status.

**Parameters**: None

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "FastAPI Metrics Monitoring System",
  "version": "1.0.0"
}
```

**Status Codes**:
- `200 OK`: Application is healthy

**Example**:
```bash
curl -X GET "http://localhost:8000/health"
```

#### GET /health/detailed

**Description**: Comprehensive health check with system metrics and process information.

**Parameters**: None

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "FastAPI Metrics Monitoring System",
  "version": "1.0.0",
  "system": {
    "cpu_percent": 15.2,
    "memory": {
      "total": 8589934592,
      "available": 4294967296,
      "percent": 50.0,
      "used": 4294967296,
      "free": 4294967296
    },
    "disk": {
      "total": 107374182400,
      "used": 53687091200,
      "free": 53687091200,
      "percent": 50.0
    }
  },
  "process": {
    "pid": 1234,
    "memory_rss": 52428800,
    "memory_vms": 104857600,
    "cpu_percent": 2.5,
    "num_threads": 8,
    "create_time": 1705312200.0
  }
}
```

**Status Codes**:
- `200 OK`: Application is healthy with detailed metrics

**Example**:
```bash
curl -X GET "http://localhost:8000/health/detailed"
```

#### GET /health/ready

**Description**: Kubernetes readiness probe endpoint.

**Parameters**: None

**Response**:
```json
{
  "status": "ready"
}
```

**Status Codes**:
- `200 OK`: Application is ready to serve traffic

**Example**:
```bash
curl -X GET "http://localhost:8000/health/ready"
```

#### GET /health/live

**Description**: Kubernetes liveness probe endpoint.

**Parameters**: None

**Response**:
```json
{
  "status": "alive"
}
```

**Status Codes**:
- `200 OK`: Application is alive and running

**Example**:
```bash
curl -X GET "http://localhost:8000/health/live"
```

### Data Management Endpoints

#### POST /api/v1/data

**Description**: Create a new data item with automatic ID generation and timestamp tracking.

**Parameters**:

**Request Body** (JSON):
```json
{
  "name": "string",           // Required: Item name
  "value": "number",          // Required: Numeric value
  "category": "string",       // Required: Item category
  "metadata": "object"        // Optional: Additional metadata
}
```

**Response**:
```json
{
  "success": true,
  "message": "Data item created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Sample Item",
    "value": 42.5,
    "category": "test",
    "metadata": {
      "source": "api",
      "priority": "high"
    },
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T10:30:00.000Z"
  }
}
```

**Status Codes**:
- `201 Created`: Data item created successfully
- `422 Unprocessable Entity`: Validation error

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/data" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Item",
    "value": 123.45,
    "category": "example",
    "metadata": {
      "source": "curl",
      "test": true
    }
  }'
```

#### GET /api/v1/data

**Description**: Retrieve all data items with optional filtering and pagination.

**Query Parameters**:
- `category` (string, optional): Filter by category
- `limit` (integer, optional, default: 100): Maximum number of items (1-1000)
- `offset` (integer, optional, default: 0): Number of items to skip

**Response**:
```json
{
  "success": true,
  "message": "Retrieved 2 items",
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Sample Item",
        "value": 42.5,
        "category": "test",
        "metadata": {
          "source": "api"
        },
        "created_at": "2024-01-15T10:30:00.000Z",
        "updated_at": "2024-01-15T10:30:00.000Z"
      }
    ]
  },
  "count": 2
}
```

**Status Codes**:
- `200 OK`: Data retrieved successfully
- `422 Unprocessable Entity`: Invalid query parameters

**Examples**:
```bash
# Get all data
curl -X GET "http://localhost:8000/api/v1/data"

# Get data with filtering and pagination
curl -X GET "http://localhost:8000/api/v1/data?category=test&limit=10&offset=0"

# Get data with category filter only
curl -X GET "http://localhost:8000/api/v1/data?category=production"
```

#### GET /api/v1/data/{item_id}

**Description**: Retrieve a specific data item by its unique identifier.

**Path Parameters**:
- `item_id` (string, required): Unique identifier of the data item

**Response**:
```json
{
  "success": true,
  "message": "Data item retrieved successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Sample Item",
    "value": 42.5,
    "category": "test",
    "metadata": {
      "source": "api"
    },
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T10:30:00.000Z"
  }
}
```

**Status Codes**:
- `200 OK`: Data item found and returned
- `404 Not Found`: Data item not found

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/data/550e8400-e29b-41d4-a716-446655440000"
```

#### PUT /api/v1/data/{item_id}

**Description**: Update an existing data item with automatic timestamp tracking.

**Path Parameters**:
- `item_id` (string, required): Unique identifier of the data item

**Request Body** (JSON):
```json
{
  "name": "string",           // Required: Item name
  "value": "number",          // Required: Numeric value
  "category": "string",       // Required: Item category
  "metadata": "object"        // Optional: Additional metadata
}
```

**Response**:
```json
{
  "success": true,
  "message": "Data item updated successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Updated Item",
    "value": 84.0,
    "category": "updated",
    "metadata": {
      "source": "api",
      "updated": true
    },
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T10:35:00.000Z"
  }
}
```

**Status Codes**:
- `200 OK`: Data item updated successfully
- `404 Not Found`: Data item not found
- `422 Unprocessable Entity`: Validation error

**Example**:
```bash
curl -X PUT "http://localhost:8000/api/v1/data/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Test Item",
    "value": 999.99,
    "category": "updated",
    "metadata": {
      "source": "curl_update",
      "version": 2
    }
  }'
```

#### DELETE /api/v1/data/{item_id}

**Description**: Delete a data item by its unique identifier.

**Path Parameters**:
- `item_id` (string, required): Unique identifier of the data item

**Response**:
```json
{
  "success": true,
  "message": "Data item deleted successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Sample Item",
    "value": 42.5,
    "category": "test",
    "metadata": {
      "source": "api"
    },
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T10:30:00.000Z"
  }
}
```

**Status Codes**:
- `200 OK`: Data item deleted successfully
- `404 Not Found`: Data item not found

**Example**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/data/550e8400-e29b-41d4-a716-446655440000"
```

#### GET /api/v1/stats

**Description**: Get statistical information about stored data items.

**Parameters**: None

**Response**:
```json
{
  "total_items": 150,
  "categories": {
    "test": 75,
    "production": 50,
    "development": 25
  },
  "average_value": 67.3,
  "min_value": 1.0,
  "max_value": 999.9
}
```

**Status Codes**:
- `200 OK`: Statistics calculated successfully

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/stats"
```

#### POST /api/v1/simulate-load

**Description**: Simulate CPU load for testing metrics and monitoring systems.

**Query Parameters**:
- `duration` (integer, optional, default: 5): Duration in seconds (1-60)

**Response**:
```json
{
  "message": "Load simulation completed",
  "duration_seconds": 10,
  "operations_performed": 1500000,
  "start_time": "2024-01-15T10:30:00.000Z",
  "end_time": "2024-01-15T10:30:10.000Z"
}
```

**Status Codes**:
- `200 OK`: Load simulation completed
- `422 Unprocessable Entity`: Invalid duration parameter

**Examples**:
```bash
# Default 5-second load simulation
curl -X POST "http://localhost:8000/api/v1/simulate-load"

# 30-second load simulation
curl -X POST "http://localhost:8000/api/v1/simulate-load?duration=30"
```

### Metrics Endpoints

#### GET /metrics

**Description**: Prometheus metrics endpoint exposing all collected metrics in Prometheus exposition format.

**Parameters**: None

**Response**: Plain text in Prometheus format
```
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/v1/data",status_code="200"} 1234.0

# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",endpoint="/api/v1/data",le="0.005"} 100.0
http_request_duration_seconds_bucket{method="GET",endpoint="/api/v1/data",le="0.01"} 200.0
http_request_duration_seconds_bucket{method="GET",endpoint="/api/v1/data",le="0.025"} 300.0
http_request_duration_seconds_bucket{method="GET",endpoint="/api/v1/data",le="+Inf"} 1234.0
http_request_duration_seconds_sum{method="GET",endpoint="/api/v1/data"} 123.45
http_request_duration_seconds_count{method="GET",endpoint="/api/v1/data"} 1234.0

# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total 123.45

# HELP process_resident_memory_bytes Resident memory size in bytes
# TYPE process_resident_memory_bytes gauge
process_resident_memory_bytes 52428800.0
```

**Status Codes**:
- `200 OK`: Metrics generated successfully
- `500 Internal Server Error`: Error generating metrics

**Example**:
```bash
curl -X GET "http://localhost:8000/metrics"
```

#### GET /metrics/summary

**Description**: Human-readable summary of current metrics for debugging and monitoring.

**Parameters**: None

**Response**:
```json
{
  "system_metrics": {
    "process": {
      "cpu_percent": 2.5,
      "memory_rss": 52428800,
      "memory_vms": 104857600,
      "num_threads": 8
    },
    "system": {
      "cpu_percent": 15.2,
      "memory_percent": 50.0,
      "memory_available": 4294967296,
      "memory_used": 4294967296
    }
  },
  "http_metrics": {
    "active_requests": 3,
    "total_requests": "See prometheus metrics",
    "metrics_available": [
      "http_requests_total",
      "http_request_duration_seconds",
      "http_request_size_bytes",
      "http_response_size_bytes",
      "http_requests_in_progress",
      "http_requests_exceptions_total",
      "http_request_processing_seconds"
    ]
  },
  "active_requests": 3,
  "metrics_endpoint": "/metrics",
  "collection_interval": 5
}
```

**Status Codes**:
- `200 OK`: Metrics summary generated successfully
- `500 Internal Server Error`: Error getting metrics summary

**Example**:
```bash
curl -X GET "http://localhost:8000/metrics/summary"
```

## Data Models

### DataItem

```json
{
  "id": "string",                    // UUID4 format, auto-generated
  "name": "string",                  // Required, item name
  "value": "number",                 // Required, numeric value
  "category": "string",              // Required, item category
  "metadata": "object",              // Optional, additional data
  "created_at": "string",            // ISO 8601 datetime, auto-generated
  "updated_at": "string"             // ISO 8601 datetime, auto-updated
}
```

### DataResponse

```json
{
  "success": "boolean",              // Operation success status
  "message": "string",               // Human-readable message
  "data": "object",                  // Response data (optional)
  "count": "integer"                 // Total count (optional, for lists)
}
```

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing:

- **Per-IP rate limiting**: Limit requests per IP address
- **Per-endpoint rate limiting**: Different limits for different endpoints
- **Authenticated user rate limiting**: Higher limits for authenticated users

## Caching

The API currently does not implement caching. Consider adding:

- **Response caching**: Cache GET responses for better performance
- **Database query caching**: Cache frequently accessed data
- **CDN integration**: Use CDN for static content and API responses

## Versioning

The API uses URL path versioning:
- Current version: `v1`
- Base path: `/api/v1`
- Future versions will be available at `/api/v2`, etc.

## OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## SDK and Client Libraries

Currently, no official SDK is provided. You can generate client libraries using the OpenAPI specification:

```bash
# Generate Python client
openapi-generator generate -i http://localhost:8000/openapi.json -g python -o ./python-client

# Generate JavaScript client
openapi-generator generate -i http://localhost:8000/openapi.json -g javascript -o ./js-client

# Generate Go client
openapi-generator generate -i http://localhost:8000/openapi.json -g go -o ./go-client
```

## Testing

### Manual Testing

Use the provided curl examples or tools like:
- **Postman**: Import the OpenAPI specification
- **Insomnia**: Import the OpenAPI specification
- **HTTPie**: Command-line HTTP client

### Automated Testing

Example test script using Python:

```python
import requests
import json

base_url = "http://localhost:8000"

# Test health endpoint
response = requests.get(f"{base_url}/health")
assert response.status_code == 200
assert response.json()["status"] == "healthy"

# Test data creation
data = {
    "name": "Test Item",
    "value": 123.45,
    "category": "test"
}
response = requests.post(f"{base_url}/api/v1/data", json=data)
assert response.status_code == 201
item_id = res
(Content truncated due to size limit. Use line ranges to read in chunks)