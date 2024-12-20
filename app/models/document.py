from pydantic import BaseModel
from typing import Optional


class DocumentInput(BaseModel):
    content: str
    metadata: Optional[dict] = None


class DocumentOutput(BaseModel):
    id: str
    content: str
    metadata: Optional[dict] = None
    similarity_score: Optional[float] = None
