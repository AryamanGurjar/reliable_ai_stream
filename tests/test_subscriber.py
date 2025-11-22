"""Test subscriber."""

import pytest
from reliable_ai_streams import Subscriber, Config


def test_subscriber_connect():
    """Test connection."""
    config = Config(bootstrap_servers="localhost:9092")
    subscriber = Subscriber(config)
    
    subscriber.connect()
    assert subscriber.consumer is not None
    
    subscriber.disconnect()


def test_subscriber_context_manager():
    """Test context manager."""
    config = Config(bootstrap_servers="localhost:9092")
    
    with Subscriber(config) as subscriber:
        assert subscriber.consumer is not None
