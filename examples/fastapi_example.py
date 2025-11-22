"""FastAPI integration example."""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

from reliable_ai_streams import Publisher, Subscriber, Config, Chunk


app = FastAPI()

# Initialize
config = Config()
publisher = Publisher(config)
subscriber = Subscriber(config)


@app.on_event("startup")
def startup():
    """Connect on startup."""
    publisher.connect()
    subscriber.connect()


@app.on_event("shutdown")
def shutdown():
    """Disconnect on shutdown."""
    publisher.disconnect()
    subscriber.disconnect()


class ChatRequest(BaseModel):
    """Chat request."""
    conversation_id: str
    message: str


@app.post("/chat")
async def chat(request: ChatRequest):
    """Start AI generation."""
    
    async def generate():
        """Simulate AI response."""
        response = f"You said: {request.message}"
        
        for word in response.split():
            yield Chunk(
                conversation_id=request.conversation_id,
                content=word + " ",
                type="text"
            )
            await asyncio.sleep(0.1)
        
        yield Chunk(
            conversation_id=request.conversation_id,
            content="",
            type="finish"
        )
    
    # Publish in background
    asyncio.create_task(
        publisher.publish_stream(request.conversation_id, generate())
    )
    
    return {"conversation_id": request.conversation_id}


@app.get("/stream/{conversation_id}")
def stream(conversation_id: str, from_offset: int = None):
    """Stream AI response via SSE."""
    
    def event_stream():
        """Generate SSE events."""
        for chunk in subscriber.subscribe(conversation_id, from_offset):
            yield f"data: {chunk.to_json().decode()}\n\n"
            
            if chunk.type == "finish":
                break
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
