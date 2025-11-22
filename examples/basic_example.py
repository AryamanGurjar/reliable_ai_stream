"""Basic usage example."""

import asyncio
from reliable_ai_streams import Publisher, Subscriber, Config, Chunk


async def generate_ai_response(conversation_id: str):
    """Simulate AI generating a response."""
    words = ["Hello", "there!", "How", "can", "I", "help", "you?"]
    
    for word in words:
        yield Chunk(
            conversation_id=conversation_id,
            content=word + " ",
            type="text"
        )
        await asyncio.sleep(0.3)  # Simulate generation delay
    
    # Send finish signal
    yield Chunk(
        conversation_id=conversation_id,
        content="",
        type="finish"
    )


async def main():
    """Run example."""
    config = Config()
    conversation_id = "demo-123"
    
    # Publish (backend)
    print("Publishing AI response...")
    with Publisher(config) as publisher:
        chunks = generate_ai_response(conversation_id)
        await publisher.publish_stream(conversation_id, chunks)
    
    print("Done publishing!\n")
    
    # Subscribe (frontend)
    print("Subscribing to stream...")
    with Subscriber(config) as subscriber:
        for chunk in subscriber.subscribe(conversation_id):
            print(f"Received: '{chunk.content}' (type: {chunk.type})")
            
            if chunk.type == "finish":
                print("\nStream complete!")
                break


if __name__ == "__main__":
    asyncio.run(main())
