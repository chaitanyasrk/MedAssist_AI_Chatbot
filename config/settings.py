"""
Configuration settings for the Troubleshooting Chatbot API
"""

import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Azure OpenAI Configuration (only for chat, not embeddings)
    azure_openai_endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(..., env="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field(default="2024-02-01", env="AZURE_OPENAI_API_VERSION")
    azure_openai_deployment_name: str = Field(..., env="AZURE_OPENAI_DEPLOYMENT_NAME")
    
    # Embedding Configuration - Using local SentenceTransformer
    embedding_model_name: str = Field(default="thenlper/gte-large", env="EMBEDDING_MODEL_NAME")
    
    # Vector Database Configuration
    vector_db_path: str = Field(default="./data/vectordb", env="VECTOR_DB_PATH")
    collection_name: str = Field(default="troubleshooting_docs", env="COLLECTION_NAME")
    
    # Chat Configuration
    max_context_length: int = Field(default=4000, env="MAX_CONTEXT_LENGTH")
    temperature: float = Field(default=0.3, env="TEMPERATURE")
    max_tokens: int = Field(default=1000, env="MAX_TOKENS")
    similarity_threshold: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")
    top_k_results: int = Field(default=5, env="TOP_K_RESULTS")
    
    # API Configuration
    api_timeout: int = Field(default=30, env="API_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    
    # Security Configuration
    enable_guardrails: bool = Field(default=True, env="ENABLE_GUARDRAILS")
    guardrails_config_path: str = Field(default="./config/guardrails_config.yml", env="GUARDRAILS_CONFIG_PATH")
    
    # Evaluation Configuration
    golden_dataset_path: str = Field(default="./data/golden_dataset.json", env="GOLDEN_DATASET_PATH")
    evaluation_metrics_path: str = Field(default="./data/evaluation_metrics.json", env="EVALUATION_METRICS_PATH")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="ALLOWED_ORIGINS"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()