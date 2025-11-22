"""Data models."""

from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class Chunk(BaseModel):
    """A single chunk in the AI stream."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    content: str
    type: Literal["text", "finish", "error"] = "text"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def to_json(self) -> bytes:
        """Convert to JSON bytes."""
        import orjson
        return orjson.dumps({
            "id": self.id,
            "conversation_id": self.conversation_id,
            "content": self.content,
            "type": self.type,
            "timestamp": self.timestamp.isoformat(),
        })
    
    @classmethod
    def from_json(cls, data: bytes) -> "Chunk":
        """Create from JSON bytes."""
        import orjson
        obj = orjson.loads(data)
        obj["timestamp"] = datetime.fromisoformat(obj["timestamp"])
        return cls(**obj)
