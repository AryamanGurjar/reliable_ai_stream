"""Frontend Client - Simulates frontend receiving AI responses from Kafka."""

import time
import sys
from reliable_ai_streams import Subscriber, Config


class FrontendClient:
    """Simulates a frontend client receiving AI responses."""
    
    def __init__(self, client_id: str = "frontend-1"):
        self.client_id = client_id
        self.config = Config(
            bootstrap_servers="localhost:9092",
            replication_factor=1
        )
        self.subscriber = Subscriber(
            self.config,
            group_id=f"frontend-group-{client_id}"
        )
    
    def connect(self):
        """Connect to Kafka."""
        self.subscriber.connect()
        print(f"🖥️  Frontend Client [{self.client_id}] started")
        print(f"📡 Connected to Kafka at localhost:9092")
        print("=" * 60)
    
    def disconnect(self):
        """Disconnect from Kafka."""
        self.subscriber.disconnect()
        print(f"\n🛑 Frontend Client [{self.client_id}] stopped")
    
    def stream_response(self, conversation_id: str, from_offset: int = None):
        """
        Stream AI response for a conversation.
        
        Args:
            conversation_id: Conversation ID to subscribe to
            from_offset: Optional offset to replay from
        """
        print(f"\n🎧 Listening to conversation: {conversation_id}")
        if from_offset is not None:
            print(f"   📍 Starting from offset: {from_offset}")
        print("-" * 60)
        
        full_response = ""
        chunk_count = 0
        start_time = time.time()
        
        try:
            for chunk in self.subscriber.subscribe(conversation_id, from_offset):
                chunk_count += 1
                
                if chunk.type == "text":
                    # Display chunk in real-time
                    print(chunk.content, end="", flush=True)
                    full_response += chunk.content
                
                elif chunk.type == "error":
                    print(f"\n❌ Error: {chunk.content}")
                    break
                
                elif chunk.type == "finish":
                    elapsed = time.time() - start_time
                    print(f"\n\n✅ Stream complete!")
                    print(f"   📊 Received {chunk_count} chunks in {elapsed:.2f}s")
                    print(f"   📝 Full response: {len(full_response)} characters")
                    break
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Stream interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def replay_conversation(self, conversation_id: str):
        """Replay a conversation from the beginning."""
        print(f"\n🔄 Replaying conversation: {conversation_id}")
        self.stream_response(conversation_id, from_offset=0)
    
    def watch_multiple_conversations(self, conversation_ids: list):
        """Watch multiple conversations sequentially."""
        for conv_id in conversation_ids:
            self.stream_response(conv_id)
            print("\n" + "=" * 60)


def main():
    """Run frontend client."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python frontend_client.py <conversation_id>")
        print("  python frontend_client.py conv-001")
        print("  python frontend_client.py conv-001 conv-002 conv-003")
        print("\nOr run in interactive mode:")
        print("  python frontend_client.py interactive")
        sys.exit(1)
    
    client = FrontendClient()
    client.connect()
    
    try:
        if sys.argv[1] == "interactive":
            # Interactive mode
            print("\n🎯 Interactive Mode")
            print("=" * 60)
            
            while True:
                conv_id = input("\nEnter conversation ID (or 'quit'): ").strip()
                if conv_id.lower() in ['quit', 'exit', 'q']:
                    break
                
                replay = input("Replay from start? (y/n): ").strip().lower()
                offset = 0 if replay == 'y' else None
                
                client.stream_response(conv_id, from_offset=offset)
        else:
            # Watch specified conversations
            conversation_ids = sys.argv[1:]
            client.watch_multiple_conversations(conversation_ids)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Shutting down...")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
