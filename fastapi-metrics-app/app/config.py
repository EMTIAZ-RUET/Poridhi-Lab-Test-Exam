"""
Configuration management for FastAPI Metrics Application
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    app_name: str = "FastAPI Metrics Monitoring System"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Supabase settings
    supabase_url: str = "https://rrruedskgtywicwholhp.supabase.co"
    supabase_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJycnVlZHNrZ3R5d2ljd2hvbGhwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTExNzY3ODEsImV4cCI6MjA2Njc1Mjc4MX0.w-mOsCBwi1Kw2sPVTguB5i6u0PhgE-FB4eVbJ7-y96A"
    supabase_table: str = "data_items"
    
    # Metrics settings
    metrics_path: str = "/metrics"
    metrics_collection_interval: int = 5  # seconds
    
    # Histogram buckets for request duration
    request_duration_buckets: List[float] = [
        0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0
    ]
    
    # CORS settings
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()