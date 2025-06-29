"""
Metrics middleware for FastAPI
Automatically tracks HTTP requests and integrates with Prometheus metrics
"""
import time
import logging
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.metrics.http_metrics import http_collector

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect HTTP metrics for all requests
    """
    
    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[list] = None,
        group_paths: bool = True
    ):
        """
        Initialize metrics middleware
        
        Args:
            app: ASGI application
            exclude_paths: List of paths to exclude from metrics collection
            group_paths: Whether to group similar paths (e.g., /api/v1/data/{id})
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/metrics", "/docs", "/redoc", "/openapi.json"]
        self.group_paths = group_paths
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and collect metrics
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/handler in chain
            
        Returns:
            Response object
        """
        # Extract request information
        method = request.method
        path = request.url.path
        
        # Check if path should be excluded
        if self._should_exclude_path(path):
            return await call_next(request)
        
        # Group similar paths if enabled
        endpoint = self._group_path(path) if self.group_paths else path
        
        # Get request size
        request_size = self._get_request_size(request)
        
        # Start tracking request
        request_id = http_collector.start_request(method, endpoint, request_size)
        
        # Process request
        start_time = time.time()
        exception_type = None
        status_code = 500  # Default to error status
        response_size = None
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            response_size = self._get_response_size(response)
            
        except Exception as e:
            exception_type = type(e).__name__
            logger.error(f"Exception in request {method} {path}: {e}")
            # Re-raise the exception to maintain normal error handling
            raise
        
        finally:
            # End tracking request
            http_collector.end_request(
                request_id=request_id,
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                response_size=response_size,
                exception_type=exception_type
            )
            
            # Log request details
            duration = time.time() - start_time
            logger.info(
                f"{method} {path} - {status_code} - {duration:.3f}s"
                f"{f' - {request_size}B req' if request_size else ''}"
                f"{f' - {response_size}B resp' if response_size else ''}"
            )
        
        return response
    
    def _should_exclude_path(self, path: str) -> bool:
        """
        Check if path should be excluded from metrics collection
        
        Args:
            path: Request path
            
        Returns:
            True if path should be excluded
        """
        return any(excluded in path for excluded in self.exclude_paths)
    
    def _group_path(self, path: str) -> str:
        """
        Group similar paths for better metrics aggregation
        
        Args:
            path: Original request path
            
        Returns:
            Grouped path
        """
        # Common path grouping patterns
        import re
        
        # Replace UUIDs with {id}
        path = re.sub(
            r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '/{id}',
            path,
            flags=re.IGNORECASE
        )
        
        # Replace numeric IDs with {id}
        path = re.sub(r'/\d+', '/{id}', path)
        
        # Replace other common patterns
        path = re.sub(r'/[a-zA-Z0-9_-]{20,}', '/{token}', path)
        
        return path
    
    def _get_request_size(self, request: Request) -> Optional[int]:
        """
        Get request body size
        
        Args:
            request: FastAPI request object
            
        Returns:
            Request size in bytes or None if not available
        """
        try:
            content_length = request.headers.get("content-length")
            if content_length:
                return int(content_length)
        except (ValueError, TypeError):
            pass
        return None
    
    def _get_response_size(self, response: Response) -> Optional[int]:
        """
        Get response body size
        
        Args:
            response: FastAPI response object
            
        Returns:
            Response size in bytes or None if not available
        """
        try:
            content_length = response.headers.get("content-length")
            if content_length:
                return int(content_length)
            
            # Try to get size from body if available
            if hasattr(response, 'body') and response.body:
                return len(response.body)
                
        except (ValueError, TypeError, AttributeError):
            pass
        return None


class MetricsCleanupMiddleware:
    """
    Background task to clean up stale metrics
    """
    
    def __init__(self, cleanup_interval: int = 300, max_request_age: int = 300):
        """
        Initialize cleanup middleware
        
        Args:
            cleanup_interval: How often to run cleanup in seconds
            max_request_age: Maximum age for active requests in seconds
        """
        self.cleanup_interval = cleanup_interval
        self.max_request_age = max_request_age
        self._running = False
    
    async def start_cleanup(self):
        """Start the cleanup background task"""
        import asyncio
        
        self._running = True
        logger.info(f"Starting metrics cleanup task (interval: {self.cleanup_interval}s)")
        
        while self._running:
            try:
                http_collector.cleanup_stale_requests(self.max_request_age)
                await asyncio.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"Error in metrics cleanup: {e}")
                await asyncio.sleep(self.cleanup_interval)
    
    def stop_cleanup(self):
        """Stop the cleanup background task"""
        self._running = False
        logger.info("Stopping metrics cleanup task")


# Global cleanup instance
metrics_cleanup = MetricsCleanupMiddleware()