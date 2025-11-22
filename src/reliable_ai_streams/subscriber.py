"""Kafka subscriber for AI streams."""

from typing import Iterator, Optional
from confluent_kafka import Consumer, KafkaError, TopicPartition

from .config import Config
from .models import Chunk


class Subscriber:
    """Subscribes to AI streams from Kafka."""
    
    def __init__(self, config: Optional[Config] = None, group_id: str = "ai-stream-subscriber"):
        """
        Initialize subscriber.
        
        Args:
            config: Configuration (loads from env if not provided)
            group_id: Consumer group ID
        """
        self.config = config or Config()
        self.group_id = group_id
        self.consumer: Optional[Consumer] = None
    
    def connect(self) -> None:
        """Connect to Kafka."""
        kafka_config = self.config.kafka_config()
        
        # Consumer config
        consumer_config = {
            **kafka_config,
            "group.id": self.group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": "false",
        }
        
        self.consumer = Consumer(consumer_config)
    
    def disconnect(self) -> None:
        """Disconnect from Kafka."""
        if self.consumer:
            self.consumer.close()
    
    def subscribe(
        self, 
        conversation_id: str, 
        from_offset: Optional[int] = None
    ) -> Iterator[Chunk]:
        """
        Subscribe to a conversation stream.
        
        Args:
            conversation_id: Conversation ID
            from_offset: Optional offset to start from
            
        Yields:
            Chunks from the stream
        """
        topic = f"{self.config.topic_prefix}-{conversation_id}"
        
        # Subscribe
        self.consumer.subscribe([topic])
        
        # Seek to offset if specified
        if from_offset is not None:
            # Wait for assignment
            while not self.consumer.assignment():
                self.consumer.poll(0.1)
            
            # Seek
            tp = TopicPartition(topic, 0, from_offset)
            self.consumer.seek(tp)
        
        # Consume messages
        try:
            while True:
                msg = self.consumer.poll(1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        raise Exception(f"Kafka error: {msg.error()}")
                
                # Parse chunk
                chunk = Chunk.from_json(msg.value())
                
                # Commit offset
                self.consumer.commit(asynchronous=False)
                
                yield chunk
                
                # Stop if finish chunk
                if chunk.type == "finish":
                    break
        
        finally:
            self.consumer.unsubscribe()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, *args):
        """Context manager exit."""
        self.disconnect()
