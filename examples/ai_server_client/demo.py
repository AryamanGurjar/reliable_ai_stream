"""Complete demo - Run both server and client."""

import asyncio
import subprocess
import time
import sys


def run_server():
    """Run AI server in background."""
    print("🚀 Starting AI Server...")
    server = subprocess.Popen(
        [sys.executable, "ai_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(2)  # Let server start
    return server


def run_client(conversation_ids):
    """Run frontend client."""
    print("\n🚀 Starting Frontend Client...")
    time.sleep(3)  # Wait for AI to generate some content
    
    subprocess.run(
        [sys.executable, "frontend_client.py"] + conversation_ids
    )


def main():
    """Run complete demo."""
    print("=" * 60)
    print("🎬 AI Streaming Demo")
    print("=" * 60)
    
    server = None
    try:
        # Start server
        server = run_server()
        
        # Run client
        run_client(["conv-001", "conv-002", "conv-003"])
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    finally:
        if server:
            print("\n🛑 Stopping server...")
            server.terminate()
            server.wait()
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    main()
