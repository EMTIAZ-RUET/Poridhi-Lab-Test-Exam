"""
Health check endpoints for monitoring application status
"""
from fastapi import APIRouter, status
from datetime import datetime
import psutil
import os
from typing import Dict, Any

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    Returns application status and basic system information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "FastAPI Metrics Monitoring System",
        "version": "1.0.0"
    }


@router.get("/health/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with system metrics
    Returns comprehensive system and application status
    """
    # Get system information
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Get process information
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "FastAPI Metrics Monitoring System",
        "version": "1.0.0",
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        },
        "process": {
            "pid": process.pid,
            "memory_rss": process_memory.rss,
            "memory_vms": process_memory.vms,
            "cpu_percent": process.cpu_percent(),
            "num_threads": process.num_threads(),
            "create_time": process.create_time()
        }
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, str]:
    """
    Kubernetes readiness probe endpoint
    """
    try:
        # Check database connectivity
        db_healthy = await db_client.health_check()
        if db_healthy:
            return {"status": "ready"}
        else:
            return {"status": "not ready", "reason": "database not healthy"}
    except Exception as e:
        return {"status": "not ready", "reason": f"database check failed: {str(e)}"}


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, str]:
    """
    Kubernetes liveness probe endpoint
    """
    return {"status": "alive"}