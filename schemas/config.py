"""Configuration management for Security AI Platform."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class AWSConfig(BaseSettings):
    """AWS and S3 configuration."""
    
    access_key_id: str = ""
    secret_access_key: str = ""
    default_region: str = "us-east-1"
    s3_bucket_raw: str = "sec-ai-raw"
    s3_bucket_features: str = "sec-ai-features"
    s3_bucket_models: str = "sec-ai-models"

    class Config:
        env_prefix = "AWS_"


class KafkaConfig(BaseSettings):
    """Kafka streaming configuration."""
    
    bootstrap_servers: str = "localhost:9092"
    topic_netflow: str = "sec.netflow"
    topic_logs: str = "sec.logs"
    topic_email: str = "sec.email"
    topic_auth: str = "sec.auth"
    topic_malware: str = "sec.malware"
    topic_alerts: str = "sec.alerts"
    consumer_group: str = "sec-ai-consumers"

    class Config:
        env_prefix = "KAFKA_"


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    
    # Postgres
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "secai_metadata"
    postgres_user: str = "secai"
    postgres_password: str = "changeme"
    
    # ClickHouse
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 9000
    clickhouse_db: str = "secai"
    clickhouse_user: str = "default"
    clickhouse_password: str = ""
    
    # Elasticsearch
    elasticsearch_host: str = "localhost"
    elasticsearch_port: int = 9200
    elasticsearch_user: str = "elastic"
    elasticsearch_password: str = "changeme"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    class Config:
        env_prefix = ""


class MLflowConfig(BaseSettings):
    """MLflow and model registry configuration."""
    
    tracking_uri: str = "http://localhost:5000"
    experiment_prefix: str = "sec-ai"
    artifact_root: str = "s3://sec-ai-models/mlflow"
    
    class Config:
        env_prefix = "MLFLOW_"


class InferenceConfig(BaseSettings):
    """Model inference configuration."""
    
    model_cache_dir: str = "/tmp/sec-ai-models"
    inference_timeout_seconds: int = 30
    batch_size: int = 32
    enable_shap: bool = True
    shap_sample_size: int = 100

    class Config:
        env_prefix = ""


class SecurityConfig(BaseSettings):
    """Security and authentication configuration."""
    
    api_key_header: str = "X-API-Key"
    jwt_secret_key: str = "your_jwt_secret_change_me"
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = 60
    allowed_origins: str = "*"

    class Config:
        env_prefix = ""


class AppConfig(BaseSettings):
    """Main application configuration."""
    
    log_level: str = "INFO"
    log_format: str = "json"
    environment: str = "development"
    
    # Sub-configs
    aws: AWSConfig = AWSConfig()
    kafka: KafkaConfig = KafkaConfig()
    database: DatabaseConfig = DatabaseConfig()
    mlflow: MLflowConfig = MLflowConfig()
    inference: InferenceConfig = InferenceConfig()
    security: SecurityConfig = SecurityConfig()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_config() -> AppConfig:
    """Get cached application configuration."""
    return AppConfig()
