"""Configuration management."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Configuration for Kafka streaming."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="KAFKA_",
        case_sensitive=False,
    )
    
    # Kafka connection
    bootstrap_servers: str = Field(
        default="localhost:9092",
        description="Kafka bootstrap servers (comma-separated)"
    )
    
    # Security (optional)
    security_protocol: str = Field(default="PLAINTEXT")
    sasl_mechanism: Optional[str] = Field(default=None)
    sasl_username: Optional[str] = Field(default=None)
    sasl_password: Optional[str] = Field(default=None)
    
    # Topic settings
    topic_prefix: str = Field(default="ai-stream", description="Prefix for topics")
    num_partitions: int = Field(default=1, description="Partitions per topic")
    replication_factor: int = Field(default=3, description="Replication factor")
    
    # Message settings
    retention_hours: int = Field(default=168, description="Message retention (hours)")
    compression: bool = Field(default=True, description="Enable compression")
    
    def kafka_config(self) -> dict:
        """Get Kafka client configuration."""
        config = {
            "bootstrap.servers": self.bootstrap_servers,
            "security.protocol": self.security_protocol,
        }
        
        if self.sasl_mechanism:
            config.update({
                "sasl.mechanism": self.sasl_mechanism,
                "sasl.username": self.sasl_username,
                "sasl.password": self.sasl_password,
            })
        
        return config
