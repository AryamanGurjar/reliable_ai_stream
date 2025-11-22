# Reliable AI Streams

Simple Kafka-based reliable streaming for AI applications. Handles reconnections, replays, and ensures no message loss.

## Features

- ✅ Reliable streaming (survives page refreshes)
- ✅ Replay from any point
- ✅ Simple API
- ✅ Production-ready
- ✅ Type-safe

## Installation

```bash
pip install reliable-ai-streams
```

## Quick Start

```python
from reliable_ai_streams import Publisher, Subscriber, Chunk

# Publish
with Publisher() as pub:
    chunk = Chunk(
        conversation_id="chat-123",
        content="Hello!",
        type="text"
    )
    pub.publish(chunk)

# Subscribe
with Subscriber() as sub:
    for chunk in sub.subscribe("chat-123"):
        print(chunk.content)
        if chunk.type == "finish":
            break
```

## Configuration

Set via environment variables:

```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_PREFIX=ai-stream
```

Or pass directly:

```python
from reliable_ai_streams import Config, Publisher

config = Config(bootstrap_servers="kafka:9092")
publisher = Publisher(config)
```

## FastAPI Example

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from reliable_ai_streams import Publisher, Subscriber

app = FastAPI()
publisher = Publisher()
subscriber = Subscriber()

@app.on_event("startup")
def startup():
    publisher.connect()
    subscriber.connect()

@app.get("/stream/{conversation_id}")
def stream(conversation_id: str):
    def events():
        for chunk in subscriber.subscribe(conversation_id):
            yield f"data: {chunk.to_json().decode()}\n\n"
    
    return StreamingResponse(events(), media_type="text/event-stream")
```

## License

MIT
```

## Installation & Usage

```bash
# Development setup
git clone <your-repo>
cd reliable-ai-streams

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"

# Setup environment
cp .env.example .env
# Edit .env with your Kafka settings

# Run example
python examples/basic_example.py

# Run tests (requires Kafka running)
pytest
```
