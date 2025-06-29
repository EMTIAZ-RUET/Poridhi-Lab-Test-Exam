"""
System metrics collector for Prometheus monitoring
Collects CPU, memory, and other system-level metrics
"""
import time
import psutil
import os
from prometheus_client import Gauge, Counter, Info
from typing import Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

# System metrics
process_cpu_seconds_total = Counter(
    'process_cpu_seconds_total',
    'Total user and system CPU time spent in seconds'
)

process_resident_memory_bytes = Gauge(
    'process_resident_memory_bytes',
    'Resident memory size in bytes'
)

process_virtual_memory_bytes = Gauge(
    'process_virtual_memory_bytes',
    'Virtual memory size in bytes'
)

process_start_time_seconds = Gauge(
    'process_start_time_seconds',
    'Start time of the process since unix epoch in seconds'
)

process_open_fds = Gauge(
    'process_open_fds',
    'Number of open file descriptors'
)

process_max_fds = Gauge(
    'process_max_fds',
    'Maximum number of open file descriptors'
)

# System-wide metrics
system_cpu_usage_percent = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

system_memory_usage_bytes = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes',
    ['type']  # total, available, used, free
)

system_disk_usage_bytes = Gauge(
    'system_disk_usage_bytes',
    'System disk usage in bytes',
    ['type']  # total, used, free
)

# Application info
app_info = Info(
    'app_info',
    'Application information'
)


class SystemMetricsCollector:
    """
    Collects and updates system-level metrics
    """
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()
        self._last_cpu_times = None
        self._running = False
        
        # Set application info
        app_info.info({
            'version': '1.0.0',
            'name': 'FastAPI Metrics Monitoring System',
            'python_version': f"{psutil.PYTHON_VERSION}",
        })
        
        # Set process start time
        process_start_time_seconds.set(self.process.create_time())
    
    async def start_collection(self, interval: int = 5):
        """
        Start collecting metrics at specified interval
        
        Args:
            interval: Collection interval in seconds
        """
        self._running = True
        logger.info(f"Starting system metrics collection with {interval}s interval")
        
        while self._running:
            try:
                await self.collect_metrics()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(interval)
    
    def stop_collection(self):
        """Stop metrics collection"""
        self._running = False
        logger.info("Stopping system metrics collection")
    
    async def collect_metrics(self):
        """
        Collect all system metrics
        """
        try:
            # Process metrics
            await self._collect_process_metrics()
            
            # System metrics
            await self._collect_system_metrics()
            
        except Exception as e:
            logger.error(f"Error in collect_metrics: {e}")
    
    async def _collect_process_metrics(self):
        """Collect process-specific metrics"""
        try:
            # CPU metrics
            cpu_times = self.process.cpu_times()
            total_cpu_time = cpu_times.user + cpu_times.system
            
            if self._last_cpu_times is not None:
                cpu_delta = total_cpu_time - self._last_cpu_times
                process_cpu_seconds_total.inc(cpu_delta)
            
            self._last_cpu_times = total_cpu_time
            
            # Memory metrics
            memory_info = self.process.memory_info()
            process_resident_memory_bytes.set(memory_info.rss)
            process_virtual_memory_bytes.set(memory_info.vms)
            
            # File descriptor metrics
            try:
                num_fds = self.process.num_fds()
                process_open_fds.set(num_fds)
                
                # Get max FDs from system limits
                import resource
                max_fds = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
                process_max_fds.set(max_fds)
            except (AttributeError, OSError):
                # num_fds() not available on Windows
                pass
                
        except Exception as e:
            logger.error(f"Error collecting process metrics: {e}")
    
    async def _collect_system_metrics(self):
        """Collect system-wide metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            system_cpu_usage_percent.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_memory_usage_bytes.labels(type='total').set(memory.total)
            system_memory_usage_bytes.labels(type='available').set(memory.available)
            system_memory_usage_bytes.labels(type='used').set(memory.used)
            system_memory_usage_bytes.labels(type='free').set(memory.free)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            system_disk_usage_bytes.labels(type='total').set(disk.total)
            system_disk_usage_bytes.labels(type='used').set(disk.used)
            system_disk_usage_bytes.labels(type='free').set(disk.free)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics values for debugging/monitoring
        
        Returns:
            Dictionary with current metric values
        """
        try:
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()
            system_memory = psutil.virtual_memory()
            system_cpu = psutil.cpu_percent()
            
            return {
                "process": {
                    "cpu_percent": cpu_percent,
                    "memory_rss": memory_info.rss,
                    "memory_vms": memory_info.vms,
                    "num_threads": self.process.num_threads(),
                },
                "system": {
                    "cpu_percent": system_cpu,
                    "memory_percent": system_memory.percent,
                    "memory_available": system_memory.available,
                    "memory_used": system_memory.used,
                }
            }
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {}


# Global instance
system_collector = SystemMetricsCollector()