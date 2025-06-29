"""
FastAPI Metrics Monitoring System
Main application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import uvicorn
import asyncio
import logging
from contextlib import asynccontextmanager
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.config import settings
from app.routers import health, api
from app.metrics.system_metrics import system_collector
from app.metrics.http_metrics import http_collector
from app.middleware.metrics_middleware import MetricsMiddleware, metrics_cleanup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Metrics available at: {settings.metrics_path}")
    
    # Start background tasks
    system_task = asyncio.create_task(
        system_collector.start_collection(settings.metrics_collection_interval)
    )
    cleanup_task = asyncio.create_task(metrics_cleanup.start_cleanup())
    
    logger.info("Background metrics collection started")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")
    
    # Stop background tasks
    system_collector.stop_collection()
    metrics_cleanup.stop_cleanup()
    
    # Cancel tasks
    system_task.cancel()
    cleanup_task.cancel()
    
    try:
        await system_task
    except asyncio.CancelledError:
        pass
    
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A comprehensive FastAPI application with Prometheus metrics monitoring",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Add metrics middleware
app.add_middleware(
    MetricsMiddleware,
    exclude_paths=["/metrics", "/docs", "/redoc", "/openapi.json", "/favicon.ico"],
    group_paths=True
)

# Include routers
app.include_router(health.router)
app.include_router(api.router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "metrics": settings.metrics_path,
        "api": "/api/v1"
    }


@app.get(settings.metrics_path, response_class=PlainTextResponse, tags=["Metrics"])
async def metrics():
    """
    Prometheus metrics endpoint
    Returns metrics in Prometheus exposition format
    """
    try:
        # Generate Prometheus metrics
        metrics_output = generate_latest()
        
        # Add custom headers
        response = PlainTextResponse(
            content=metrics_output.decode('utf-8'),
            media_type=CONTENT_TYPE_LATEST
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return PlainTextResponse(
            content=f"# Error generating metrics: {e}\n",
            status_code=500
        )


@app.get("/metrics/summary", tags=["Metrics"])
async def metrics_summary():
    """
    Get a summary of current metrics for debugging
    """
    try:
        return {
            "system_metrics": system_collector.get_current_metrics(),
            "http_metrics": http_collector.get_metrics_summary(),
            "active_requests": http_collector.get_active_requests_count(),
            "metrics_endpoint": settings.metrics_path,
            "collection_interval": settings.metrics_collection_interval
        }
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )