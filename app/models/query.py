from pydantic import BaseModel
from typing import Optional


class QueryInput(BaseModel):
    text: str
    limit: Optional[int] = 10
