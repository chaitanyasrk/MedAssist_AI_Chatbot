"""
Configuration settings for Medical Q&A API

This module handles all configuration loading from environment variables
and provides type-safe access to application settings.
"""

import os
import secrets
from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # ============================================================================
    # API CONFIGURATION
    # ============================================================================
    API_V1_STR: str = Field(default="/api/v1", description="API version prefix")
    PROJECT_NAME: str = Field(default="Medical Q&A API", description="Project name")
    VERSION: str = Field(default="1.0.0", description="API version")
    DESCRIPTION: str = Field(
        default="Medical Q&A API with RAG, PyTorch, and LangChain", 
        description="API description"
    )
    
    # Environment configuration
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    
    # ============================================================================
    # AZURE OPENAI CONFIGURATION
    # ============================================================================
    AZURE_OPENAI_ENDPOINT: str = Field(default="", description="Azure OpenAI endpoint URL")
    AZURE_OPENAI_API_KEY: str = Field(default="", description="Azure OpenAI API key")
    AZURE_OPENAI_API_VERSION: str = Field(
        default="2023-12-01-preview", 
        description="Azure OpenAI API version"
    )
    AZURE_OPENAI_DEPLOYMENT_NAME: str = Field(
        default="gpt-4", 
        description="Azure OpenAI GPT-4 deployment name"
    )
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = Field(
        default="text-embedding-ada-002", 
        description="Azure OpenAI embedding deployment name"
    )
    
    # LLM Generation Parameters
    DEFAULT_TEMPERATURE: float = Field(default=0.1, description="Default temperature for LLM")
    DEFAULT_MAX_TOKENS: int = Field(default=1000, description="Default max tokens for LLM")
    DEFAULT_TOP_P: float = Field(default=0.95, description="Default top_p for LLM")
    
    # ============================================================================
    # DATABASE CONFIGURATION
    # ============================================================================
    DATABASE_URL: str = Field(
        default="sqlite:///./medical_qa.db", 
        description="Database connection URL"
    )
    
    # Database pool settings (for async databases)
    DB_POOL_SIZE: int = Field(default=10, description="Database pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Database pool timeout")
    
    # ============================================================================
    # SECURITY CONFIGURATION
    # ============================================================================
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT tokens"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, 
        description="Access token expiration time in minutes"
    )
    
    # CORS settings
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Allowed CORS origins (comma-separated)"
    )
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=3600, description="Rate limit window in seconds")
    
    # ============================================================================
    # DATASET CONFIGURATION
    # ============================================================================
    DATASET_NAME: str = Field(
        default="medmcqa", 
        description="Dataset name: medmcqa or pubmed_qa"
    )
    TRAIN_SPLIT_RATIO: float = Field(
        default=0.8, 
        ge=0.1, 
        le=0.9, 
        description="Training/evaluation split ratio"
    )
    
    # ============================================================================
    # VECTOR STORE CONFIGURATION
    # ============================================================================
    VECTOR_STORE_PATH: str = Field(default="./vector_store", description="Vector store path")
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model name"
    )
    
    # Vector search parameters
    SIMILARITY_THRESHOLD: float = Field(
        default=0.7, 
        ge=0.0, 
        le=1.0, 
        description="Similarity threshold for vector search"
    )
    MAX_CONTEXT_DOCUMENTS: int = Field(
        default=5, 
        ge=1, 
        le=20, 
        description="Maximum context documents to retrieve"
    )
    
    # ============================================================================
    # LOGGING CONFIGURATION
    # ============================================================================
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: Optional[str] = Field(default=None, description="Log file path")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # ============================================================================
    # EVALUATION CONFIGURATION
    # ============================================================================
    EVALUATION_BATCH_SIZE: int = Field(default=10, description="Evaluation batch size")
    EVALUATION_TIMEOUT: int = Field(default=300, description="Evaluation timeout in seconds")
    
    # Evaluation weights
    RELEVANCE_WEIGHT: float = Field(default=0.25, description="Relevance score weight")
    ACCURACY_WEIGHT: float = Field(default=0.30, description="Accuracy score weight")
    COMPLETENESS_WEIGHT: float = Field(default=0.20, description="Completeness score weight")
    SAFETY_WEIGHT: float = Field(default=0.15, description="Safety score weight")
    CONTEXT_WEIGHT: float = Field(default=0.10, description="Context utilization weight")
    
    # ============================================================================
    # MEDICAL VALIDATION CONFIGURATION
    # ============================================================================
    MEDICAL_CONFIDENCE_THRESHOLD: float = Field(
        default=0.1, 
        ge=0.0, 
        le=1.0, 
        description="Minimum confidence for medical query validation"
    )
    
    # ============================================================================
    # OPTIONAL: ADDITIONAL SERVICES
    # ============================================================================
    # Azure Content Safety (alternative to NVIDIA Guardrails)
    AZURE_CONTENT_SAFETY_ENDPOINT: Optional[str] = Field(
        default=None, 
        description="Azure Content Safety endpoint"
    )
    AZURE_CONTENT_SAFETY_KEY: Optional[str] = Field(
        default=None, 
        description="Azure Content Safety API key"
    )
    
    # Redis (for caching, if needed)
    REDIS_URL: Optional[str] = Field(default=None, description="Redis connection URL")
    CACHE_TTL: int = Field(default=3600, description="Cache TTL in seconds")
    
    # ============================================================================
    # VALIDATORS (Updated for Pydantic v2)
    # ============================================================================
    
    @field_validator("AZURE_OPENAI_ENDPOINT")
    @classmethod
    def validate_azure_endpoint(cls, v):
        """Validate Azure OpenAI endpoint format"""
        if v and not v.startswith("https://"):
            raise ValueError("Azure OpenAI endpoint must start with https://")
        if v and not v.endswith("/"):
            v = v + "/"
        return v
    
    @field_validator("DATASET_NAME")
    @classmethod
    def validate_dataset_name(cls, v):
        """Validate dataset name"""
        allowed_datasets = ["medmcqa", "pubmed_qa"]
        if v not in allowed_datasets:
            raise ValueError(f"Dataset must be one of: {allowed_datasets}")
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level"""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()
    
    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v):
        """Validate CORS origins"""
        if isinstance(v, str):
            # Split comma-separated string and clean up
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            return origins
        elif isinstance(v, list):
            return v
        else:
            return ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    @field_validator("TRAIN_SPLIT_RATIO")
    @classmethod
    def validate_split_ratio(cls, v):
        """Validate train split ratio"""
        if not 0.1 <= v <= 0.9:
            raise ValueError("Train split ratio must be between 0.1 and 0.9")
        return v
    
    # ============================================================================
    # COMPUTED PROPERTIES
    # ============================================================================
    
    @property
    def database_url_async(self) -> str:
        """Get async database URL"""
        if self.DATABASE_URL.startswith("sqlite://"):
            return self.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
        elif self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return self.DATABASE_URL
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def vector_store_full_path(self) -> str:
        """Get full path for vector store"""
        return os.path.abspath(self.VECTOR_STORE_PATH)
    
    @property
    def evaluation_weights(self) -> dict:
        """Get evaluation weights as dictionary"""
        return {
            "relevance": self.RELEVANCE_WEIGHT,
            "accuracy": self.ACCURACY_WEIGHT,
            "completeness": self.COMPLETENESS_WEIGHT,
            "safety": self.SAFETY_WEIGHT,
            "context": self.CONTEXT_WEIGHT
        }
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def get_azure_openai_config(self) -> dict:
        """Get Azure OpenAI configuration as dictionary"""
        return {
            "api_key": self.AZURE_OPENAI_API_KEY,
            "api_version": self.AZURE_OPENAI_API_VERSION,
            "azure_endpoint": self.AZURE_OPENAI_ENDPOINT,
            "deployment_name": self.AZURE_OPENAI_DEPLOYMENT_NAME,
            "embedding_deployment": self.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        }
    
    def get_database_config(self) -> dict:
        """Get database configuration as dictionary"""
        return {
            "url": self.database_url_async,
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT
        }
    
    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS if isinstance(self.CORS_ORIGINS, list) else []
    
    def get_cors_config(self) -> dict:
        """Get CORS configuration as dictionary"""
        return {
            "allow_origins": self.get_cors_origins_list(),
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"]
        }
    
    def has_azure_openai_config(self) -> bool:
        """Check if Azure OpenAI is properly configured"""
        return bool(self.AZURE_OPENAI_ENDPOINT and self.AZURE_OPENAI_API_KEY)
    
    # ============================================================================
    # PYDANTIC CONFIGURATION
    # ============================================================================
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }


# ============================================================================
# SETTINGS INSTANCE
# ============================================================================

# Create global settings instance
try:
    settings = Settings()
except Exception as e:
    print(f"❌ Configuration Error: {e}")
    print("📝 Please check your .env file and ensure all required values are set")
    print("🔧 See .env.example for configuration template")
    
    # Create minimal settings for development
    print("🔄 Creating minimal settings for development...")
    settings = Settings(
        AZURE_OPENAI_ENDPOINT="https://example.openai.azure.com/",
        AZURE_OPENAI_API_KEY="your-key-here"
    )


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_configuration():
    """Validate critical configuration settings"""
    warnings = []
    errors = []
    
    # Check Azure OpenAI configuration
    if not settings.has_azure_openai_config():
        warnings.append("Azure OpenAI not configured - some features may not work")
    
    # Check paths exist or can be created
    try:
        os.makedirs(settings.vector_store_full_path, exist_ok=True)
    except Exception as e:
        errors.append(f"Cannot create vector store directory: {e}")
    
    # Validate evaluation weights sum to 1.0
    total_weight = sum(settings.evaluation_weights.values())
    if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
        errors.append(f"Evaluation weights must sum to 1.0, got {total_weight}")
    
    # Print warnings
    for warning in warnings:
        print(f"⚠️  Warning: {warning}")
    
    # Raise errors
    if errors:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))


# Validate configuration on import
try:
    validate_configuration()
    print("✅ Configuration loaded successfully!")
except Exception as e:
    print(f"⚠️  Configuration warnings: {e}")


# ============================================================================
# EXPORT
# ============================================================================

__all__ = ["settings", "Settings", "validate_configuration"]