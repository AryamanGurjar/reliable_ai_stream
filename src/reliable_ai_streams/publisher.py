"""Kafka publisher for AI streams."""

from typing import AsyncIterator, Optional
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

from .config import Config
from .models import Chunk


class Publisher:
    """Publishes AI chunks to Kafka."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize publisher.
        
        Args:
            config: Configuration (loads from env if not provided)
        """
        self.config = config or Config()
        self.producer: Optional[Producer] = None
        self.admin: Optional[AdminClient] = None
    
    def connect(self) -> None:
        """Connect to Kafka."""
        kafka_config = self.config.kafka_config()
        
        # Producer config
        producer_config = {
            **kafka_config,
            "acks": "all",
            "enable.idempotence": "true",
            "compression.type": "snappy" if self.config.compression else "none",
        }
        
        self.producer = Producer(producer_config)
        self.admin = AdminClient(kafka_config)
    
    def disconnect(self) -> None:
        """Disconnect from Kafka."""
        if self.producer:
            self.producer.flush()
    
    def _ensure_topic(self, topic: str) -> None:
        """Create topic if it doesn't exist."""
        metadata = self.admin.list_topics(timeout=10)
        
        if topic not in metadata.topics:
            new_topic = NewTopic(
                topic,
                num_partitions=self.config.num_partitions,
                replication_factor=self.config.replication_factor,
                config={
                    "retention.ms": str(self.config.retention_hours * 3600 * 1000),
                }
            )
            
            fs = self.admin.create_topics([new_topic])
            for _, f in fs.items():
                f.result()  # Wait for creation
    
    def publish(self, chunk: Chunk) -> None:
        """
        Publish a single chunk.
        
        Args:
            chunk: Chunk to publish
        """
        topic = f"{self.config.topic_prefix}-{chunk.conversation_id}"
        
        # Ensure topic exists
        self._ensure_topic(topic)
        
        # Publish
        self.producer.produce(
            topic=topic,
            key=chunk.conversation_id.encode("utf-8"),
            value=chunk.to_json(),
        )
        self.producer.poll(0)
    
    async def publish_stream(
        self, 
        conversation_id: str, 
        chunks: AsyncIterator[Chunk]
    ) -> None:
        """
        Publish a stream of chunks.
        
        Args:
            conversation_id: Conversation ID
            chunks: Async iterator of chunks
        """
        async for chunk in chunks:
            self.publish(chunk)
        
        self.producer.flush()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, *args):
        """Context manager exit."""
        self.disconnect()
