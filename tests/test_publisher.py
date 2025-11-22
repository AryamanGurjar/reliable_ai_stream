"""Test publisher."""

import pytest
from reliable_ai_streams import Publisher, Config, Chunk


def test_publisher_connect():
    """Test connection."""
    config = Config(bootstrap_servers="localhost:9092")
    publisher = Publisher(config)
    
    publisher.connect()
    assert publisher.producer is not None
    
    publisher.disconnect()


def test_publisher_context_manager():
    """Test context manager."""
    config = Config(bootstrap_servers="localhost:9092")
    
    with Publisher(config) as publisher:
        assert publisher.producer is not None


def test_publish_chunk():
    """Test publishing a chunk."""
    config = Config(bootstrap_servers="localhost:9092")
    
    with Publisher(config) as publisher:
        chunk = Chunk(
            conversation_id="test-123",
            content="Hello",
            type="text"
        )
        
        publisher.publish(chunk)
        # No exception = success
