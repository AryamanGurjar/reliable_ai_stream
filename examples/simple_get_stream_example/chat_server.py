"""Chat Server - Type messages and stream them to clients."""

import asyncio
from reliable_ai_streams import Publisher, Config, Chunk


class ChatServer:
    """Simple chat server that streams typed messages."""
    
    def __init__(self):
        self.config = Config(
            bootstrap_servers="localhost:9092",
            replication_factor=1
        )
        self.publisher = Publisher(self.config)
        self.publisher.connect()
    
    async def send_message(self, conversation_id: str, message: str):
        """Send a message by streaming it word by word."""
        print(f"📤 Streaming: '{message}'")
        
        # Stream word by word
        words = message.split()
        for word in words:
            chunk = Chunk(
                conversation_id=conversation_id,
                content=word + " ",
                type="text"
            )
            self.publisher.publish(chunk)
            await asyncio.sleep(0.1)  # Simulate typing speed
        
        print("✅ Message sent!\n")
    
    async def run(self):
        """Run interactive server."""
        print("=" * 60)
        print("💬 Chat Server Started")
        print("=" * 60)
        print("📡 Connected to Kafka at localhost:9092")
        print("\nInstructions:")
        print("  - Type your message and press Enter")
        print("  - Type 'quit' to exit")
        print("  - Messages will stream to clients in real-time")
        print("=" * 60)
        
        conversation_id = "chat-room-1"
        print(f"\n🎯 Chat Room: {conversation_id}\n")
        
        try:
            while True:
                # Get user input
                message = await asyncio.get_event_loop().run_in_executor(
                    None, input, "You: "
                )
                
                if message.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if message.strip():
                    await self.send_message(conversation_id, message)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Server stopped")
        finally:
            self.publisher.disconnect()


async def main():
    server = ChatServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
