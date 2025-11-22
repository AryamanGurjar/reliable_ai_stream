"""Chat Client - Receive and display streamed messages."""

import sys
from reliable_ai_streams import Subscriber, Config


class ChatClient:
    """Simple chat client that receives streamed messages."""
    
    def __init__(self, client_name: str = "Client-1"):
        self.client_name = client_name
        self.config = Config(
            bootstrap_servers="localhost:9092",
            replication_factor=1
        )
        self.subscriber = Subscriber(
            self.config,
            group_id=f"chat-client-{client_name}"
        )
        self.subscriber.connect()
    
    def listen(self, conversation_id: str):
        """Listen to chat room and display messages."""
        print("=" * 60)
        print(f"💬 Chat Client: {self.client_name}")
        print("=" * 60)
        print(f"📡 Connected to Kafka at localhost:9092")
        print(f"🎧 Listening to: {conversation_id}")
        print("\nWaiting for messages... (Press Ctrl+C to exit)\n")
        print("=" * 60)
        
        try:
            current_message = ""
            
            for chunk in self.subscriber.subscribe(conversation_id):
                if chunk.type == "text":
                    # Display chunk in real-time
                    print(chunk.content, end="", flush=True)
                    current_message += chunk.content
                    
                    # Check if message seems complete (ends with space after word)
                    if current_message.strip() and chunk.content.endswith(" "):
                        # Just continue streaming
                        pass
                
                elif chunk.type == "finish":
                    if current_message.strip():
                        print()  # New line after message
                        current_message = ""
                
                elif chunk.type == "error":
                    print(f"\n❌ Error: {chunk.content}\n")
                    current_message = ""
        
        except KeyboardInterrupt:
            print("\n\n👋 Client disconnected")
        finally:
            self.subscriber.disconnect()


def main():
    """Run chat client."""
    client_name = sys.argv[1] if len(sys.argv) > 1 else "Client-1"
    conversation_id = "chat-room-1"
    
    client = ChatClient(client_name)
    client.listen(conversation_id)


if __name__ == "__main__":
    main()
si