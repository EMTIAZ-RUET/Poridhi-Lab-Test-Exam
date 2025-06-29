"""
HTTP metrics collector for Prometheus monitoring
Tracks HTTP request patterns, performance, and response metrics
"""
import time
from prometheus_client import Counter, Histogram, Gauge
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# HTTP request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
)

http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    buckets=[64, 256, 1024, 4096, 16384, 65536, 262144, 1048576]
)

http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    buckets=[64, 256, 1024, 4096, 16384, 65536, 262144, 1048576]
)

# Current active requests
http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently being processed',
    ['method', 'endpoint']
)

# Error rate metrics
http_requests_exceptions_total = Counter(
    'http_requests_exceptions_total',
    'Total number of HTTP requests that resulted in exceptions',
    ['method', 'endpoint', 'exception_type']
)

# Additional performance metrics
http_request_processing_seconds = Histogram(
    'http_request_processing_seconds',
    'Time spent processing HTTP requests (excluding network time)',
    ['method', 'endpoint'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)


class HTTPMetricsCollector:
    """
    Collects and manages HTTP request metrics
    """
    
    def __init__(self):
        self._active_requests: Dict[str, float] = {}
    
    def start_request(self, method: str, endpoint: str, request_size: Optional[int] = None) -> str:
        """
        Start tracking a new HTTP request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: Request endpoint/path
            request_size: Size of request body in bytes
            
        Returns:
            Request ID for tracking
        """
        request_id = f"{method}:{endpoint}:{time.time()}"
        start_time = time.time()
        
        # Store request start time
        self._active_requests[request_id] = start_time
        
        # Increment active requests gauge
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
        
        # Record request size if provided
        if request_size is not None:
            http_request_size_bytes.labels(method=method, endpoint=endpoint).observe(request_size)
        
        logger.debug(f"Started tracking request: {request_id}")
        return request_id
    
    def end_request(
        self,
        request_id: str,
        method: str,
        endpoint: str,
        status_code: int,
        response_size: Optional[int] = None,
        exception_type: Optional[str] = None
    ):
        """
        End tracking of an HTTP request
        
        Args:
            request_id: Request ID from start_request
            method: HTTP method
            endpoint: Request endpoint/path
            status_code: HTTP response status code
            response_size: Size of response body in bytes
            exception_type: Type of exception if request failed
        """
        if request_id not in self._active_requests:
            logger.warning(f"Request ID {request_id} not found in active requests")
            return
        
        start_time = self._active_requests.pop(request_id)
        duration = time.time() - start_time
        
        # Update metrics
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        http_request_processing_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        # Decrement active requests gauge
        http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
        
        # Record response size if provided
        if response_size is not None:
            http_response_size_bytes.labels(
                method=method,
                endpoint=endpoint
            ).observe(response_size)
        
        # Record exception if occurred
        if exception_type:
            http_requests_exceptions_total.labels(
                method=method,
                endpoint=endpoint,
                exception_type=exception_type
            ).inc()
        
        logger.debug(f"Completed tracking request: {request_id}, duration: {duration:.3f}s")
    
    def record_exception(self, method: str, endpoint: str, exception_type: str):
        """
        Record an exception that occurred during request processing
        
        Args:
            method: HTTP method
            endpoint: Request endpoint/path
            exception_type: Type of exception
        """
        http_requests_exceptions_total.labels(
            method=method,
            endpoint=endpoint,
            exception_type=exception_type
        ).inc()
        
        logger.debug(f"Recorded exception: {exception_type} for {method} {endpoint}")
    
    def get_active_requests_count(self) -> int:
        """
        Get the number of currently active requests
        
        Returns:
            Number of active requests
        """
        return len(self._active_requests)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current HTTP metrics
        
        Returns:
            Dictionary with metrics summary
        """
        return {
            "active_requests": len(self._active_requests),
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
        }
    
    def cleanup_stale_requests(self, max_age_seconds: int = 300):
        """
        Clean up requests that have been active for too long
        This helps prevent memory leaks from requests that never complete
        
        Args:
            max_age_seconds: Maximum age for active requests in seconds
        """
        current_time = time.time()
        stale_requests = []
        
        for request_id, start_time in self._active_requests.items():
            if current_time - start_time > max_age_seconds:
                stale_requests.append(request_id)
        
        for request_id in stale_requests:
            logger.warning(f"Cleaning up stale request: {request_id}")
            self._active_requests.pop(request_id, None)
            
            # Try to extract method and endpoint from request_id
            try:
                parts = request_id.split(":", 2)
                if len(parts) >= 2:
                    method, endpoint = parts[0], parts[1]
                    http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
            except Exception as e:
                logger.error(f"Error cleaning up stale request metrics: {e}")


# Global instance
http_collector = HTTPMetricsCollector()
