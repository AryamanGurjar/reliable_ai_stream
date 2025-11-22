"""AI Server - Simulates AI generating responses and publishing to Kafka."""

import asyncio
import time
from reliable_ai_streams import Publisher, Config, Chunk


class AIServer:
    """Simulates an AI server generating responses."""
    
    def __init__(self):
        self.config = Config(
            bootstrap_servers="localhost:9092",
            replication_factor=1
        )
        self.publisher = Publisher(self.config)
    
    def start(self):
        """Start the server."""
        self.publisher.connect()
        print("🤖 AI Server started")
        print("📡 Connected to Kafka at localhost:9092")
        print("=" * 60)
    
    def stop(self):
        """Stop the server."""
        self.publisher.disconnect()
        print("\n🛑 AI Server stopped")
    
    async def generate_ai_response(self, conversation_id: str, user_message: str):
        """
        Simulate AI generating a response to user message.
        
        Args:
            conversation_id: Unique conversation ID
            user_message: User's input message
        """
        print(f"\n💬 User [{conversation_id}]: {user_message}")
        print(f"🤖 AI generating response...")
        
        # Simulate AI thinking
        await asyncio.sleep(0.5)
        
        # Generate response word by word (streaming)
        response = f"You asked about '{user_message}'. Here's my detailed response with multiple words streaming."
        words = response.split()
        
        for i, word in enumerate(words):
            # Create chunk
            chunk = Chunk(
                conversation_id=conversation_id,
                content=word + " ",
                type="text"
            )
            
            # Publish to Kafka
            self.publisher.publish(chunk)
            print(f"  📤 Sent chunk {i+1}/{len(words)}: '{word}'")
            
            # Simulate generation delay
            await asyncio.sleep(0.2)
        
        # Send finish signal
        finish_chunk = Chunk(
            conversation_id=conversation_id,
            content="",
            type="finish"
        )
        self.publisher.publish(finish_chunk)
        print(f"  ✅ Response complete!")
    
    async def handle_multiple_requests(self):
        """Simulate handling multiple user requests."""
        requests = [
            ("conv-001", "What is Kafka?"),
            ("conv-002", "How does streaming work?"),
            ("conv-003", "Tell me about AI"),
        ]
        
        for conv_id, message in requests:
            await self.generate_ai_response(conv_id, message)
            await asyncio.sleep(1)  # Pause between requests


async def main():
    """Run AI server."""
    server = AIServer()
    server.start()
    
    try:
        # Simulate handling requests
        await server.handle_multiple_requests()
        
        # Keep server running for manual testing
        print("\n" + "=" * 60)
        print("🎯 Server ready for requests!")
        print("   Conversation IDs: conv-001, conv-002, conv-003")
        print("   Press Ctrl+C to stop")
        print("=" * 60)
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Shutting down...")
    finally:
        server.stop()


if __name__ == "__main__":
    asyncio.run(main())
