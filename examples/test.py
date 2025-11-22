"""Complete test with Kafka container."""

import time
import asyncio
from reliable_ai_streams import Publisher, Subscriber, Config, Chunk


def test_basic_publish_subscribe():
    """Test basic publish and subscribe."""
    print("\n🧪 Test 1: Basic Publish/Subscribe")
    print("-" * 50)
    
    config = Config(
        bootstrap_servers="localhost:9092",
        topic_prefix="test-stream",
        num_partitions=1,
        replication_factor=1
    )
    
    conversation_id = f"test-{int(time.time())}"
    
    # Publish messages
    print(f"📤 Publishing to conversation: {conversation_id}")
    with Publisher(config) as pub:
        messages = ["Hello", "World", "from", "Kafka!"]
        
        for msg in messages:
            chunk = Chunk(
                conversation_id=conversation_id,
                content=msg,
                type="text"
            )
            pub.publish(chunk)
            print(f"  ✓ Published: {msg}")
        
        # Send finish signal
        finish_chunk = Chunk(
            conversation_id=conversation_id,
            content="",
            type="finish"
        )
        pub.publish(finish_chunk)
        print("  ✓ Published: [FINISH]")
    
    # Wait a bit for messages to be available
    time.sleep(2)
    
    # Subscribe and read messages
    print(f"\n📥 Subscribing to conversation: {conversation_id}")
    received = []
    
    with Subscriber(config, group_id=f"test-group-{int(time.time())}") as sub:
        for chunk in sub.subscribe(conversation_id):
            if chunk.type == "text":
                received.append(chunk.content)
                print(f"  ✓ Received: {chunk.content}")
            elif chunk.type == "finish":
                print("  ✓ Received: [FINISH]")
                break
    
    # Verify
    assert received == messages, f"Expected {messages}, got {received}"
    print("\n✅ Test 1 PASSED\n")


def test_replay_from_offset():
    """Test replaying from a specific offset."""
    print("\n🧪 Test 2: Replay from Offset")
    print("-" * 50)
    
    config = Config(
        bootstrap_servers="localhost:9092",
        topic_prefix="test-stream",
        num_partitions=1,
        replication_factor=1
    )
    
    conversation_id = f"replay-test-{int(time.time())}"
    
    # Publish 5 messages
    print(f"📤 Publishing 5 messages to: {conversation_id}")
    with Publisher(config) as pub:
        for i in range(5):
            chunk = Chunk(
                conversation_id=conversation_id,
                content=f"Message {i}",
                type="text"
            )
            pub.publish(chunk)
            print(f"  ✓ Published: Message {i}")
        
        finish_chunk = Chunk(
            conversation_id=conversation_id,
            content="",
            type="finish"
        )
        pub.publish(finish_chunk)
        print("  ✓ Published: [FINISH]")
    
    time.sleep(2)
    
    # Read from offset 2 (should get messages 2, 3, 4)
    print(f"\n📥 Subscribing from offset 2")
    received = []
    
    with Subscriber(config, group_id=f"replay-group-{int(time.time())}") as sub:
        for chunk in sub.subscribe(conversation_id, from_offset=2):
            if chunk.type == "text":
                received.append(chunk.content)
                print(f"  ✓ Received: {chunk.content}")
            elif chunk.type == "finish":
                print("  ✓ Received: [FINISH]")
                break
    
    # Should have received messages 2, 3, 4
    expected = ["Message 2", "Message 3", "Message 4"]
    assert received == expected, f"Expected {expected}, got {received}"
    print("\n✅ Test 2 PASSED\n")


async def test_async_streaming():
    """Test async streaming."""
    print("\n🧪 Test 3: Async Streaming")
    print("-" * 50)
    
    config = Config(
        bootstrap_servers="localhost:9092",
        topic_prefix="test-stream",
        num_partitions=1,
        replication_factor=1
    )
    
    conversation_id = f"async-test-{int(time.time())}"
    
    async def generate_chunks():
        """Simulate AI generating chunks."""
        words = ["Async", "streaming", "works", "great!"]
        for word in words:
            yield Chunk(
                conversation_id=conversation_id,
                content=word,
                type="text"
            )
            await asyncio.sleep(0.1)
        
        yield Chunk(
            conversation_id=conversation_id,
            content="",
            type="finish"
        )
    
    # Publish async
    print(f"📤 Publishing async stream to: {conversation_id}")
    with Publisher(config) as pub:
        await pub.publish_stream(conversation_id, generate_chunks())
        print("  ✓ Published async stream")
    
    time.sleep(2)
    
    # Subscribe
    print(f"\n📥 Subscribing to: {conversation_id}")
    received = []
    
    with Subscriber(config, group_id=f"async-group-{int(time.time())}") as sub:
        for chunk in sub.subscribe(conversation_id):
            if chunk.type == "text":
                received.append(chunk.content)
                print(f"  ✓ Received: {chunk.content}")
            elif chunk.type == "finish":
                print("  ✓ Received: [FINISH]")
                break
    
    expected = ["Async", "streaming", "works", "great!"]
    assert received == expected, f"Expected {expected}, got {received}"
    print("\n✅ Test 3 PASSED\n")


def test_error_handling():
    """Test error chunk handling."""
    print("\n🧪 Test 4: Error Handling")
    print("-" * 50)
    
    config = Config(
        bootstrap_servers="localhost:9092",
        topic_prefix="test-stream",
        num_partitions=1,
        replication_factor=1
    )
    
    conversation_id = f"error-test-{int(time.time())}"
    
    # Publish with error
    print(f"📤 Publishing with error to: {conversation_id}")
    with Publisher(config) as pub:
        pub.publish(Chunk(
            conversation_id=conversation_id,
            content="Starting...",
            type="text"
        ))
        print("  ✓ Published: Starting...")
        
        pub.publish(Chunk(
            conversation_id=conversation_id,
            content="Something went wrong!",
            type="error"
        ))
        print("  ✓ Published: [ERROR]")
    
    time.sleep(2)
    
    # Subscribe and handle error
    print(f"\n📥 Subscribing to: {conversation_id}")
    error_received = False
    
    with Subscriber(config, group_id=f"error-group-{int(time.time())}") as sub:
        for chunk in sub.subscribe(conversation_id):
            if chunk.type == "text":
                print(f"  ✓ Received: {chunk.content}")
            elif chunk.type == "error":
                error_received = True
                print(f"  ✓ Received ERROR: {chunk.content}")
                break
    
    assert error_received, "Error chunk not received"
    print("\n✅ Test 4 PASSED\n")


def test_multiple_subscribers():
    """Test multiple subscribers reading same stream."""
    print("\n🧪 Test 5: Multiple Subscribers")
    print("-" * 50)
    
    config = Config(
        bootstrap_servers="localhost:9092",
        topic_prefix="test-stream",
        num_partitions=1,
        replication_factor=1
    )
    
    conversation_id = f"multi-test-{int(time.time())}"
    
    # Publish messages
    print(f"📤 Publishing to: {conversation_id}")
    with Publisher(config) as pub:
        for i in range(3):
            pub.publish(Chunk(
                conversation_id=conversation_id,
                content=f"Message {i}",
                type="text"
            ))
            print(f"  ✓ Published: Message {i}")
        
        pub.publish(Chunk(
            conversation_id=conversation_id,
            content="",
            type="finish"
        ))
        print("  ✓ Published: [FINISH]")
    
    time.sleep(2)
    
    # Two subscribers with different group IDs
    print(f"\n📥 Subscriber 1:")
    received1 = []
    with Subscriber(config, group_id=f"group1-{int(time.time())}") as sub:
        for chunk in sub.subscribe(conversation_id):
            if chunk.type == "text":
                received1.append(chunk.content)
                print(f"  ✓ Received: {chunk.content}")
            elif chunk.type == "finish":
                break
    
    print(f"\n📥 Subscriber 2:")
    received2 = []
    with Subscriber(config, group_id=f"group2-{int(time.time())}") as sub:
        for chunk in sub.subscribe(conversation_id):
            if chunk.type == "text":
                received2.append(chunk.content)
                print(f"  ✓ Received: {chunk.content}")
            elif chunk.type == "finish":
                break
    
    # Both should receive all messages
    expected = ["Message 0", "Message 1", "Message 2"]
    assert received1 == expected, f"Sub1: Expected {expected}, got {received1}"
    assert received2 == expected, f"Sub2: Expected {expected}, got {received2}"
    print("\n✅ Test 5 PASSED\n")


def main():
    """Run all tests."""
    print("=" * 50)
    print("🚀 Starting Kafka Tests")
    print("=" * 50)
    
    try:
        # Test connection first
        print("\n🔌 Testing Kafka connection...")
        config = Config(bootstrap_servers="localhost:9092")
        with Publisher(config) as pub:
            print("✅ Connected to Kafka successfully!\n")
        
        # Run tests
        test_basic_publish_subscribe()
        test_replay_from_offset()
        asyncio.run(test_async_streaming())
        test_error_handling()
        test_multiple_subscribers()
        
        print("=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
