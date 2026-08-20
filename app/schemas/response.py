from pydantic import BaseModel
from typing import Any
from datetime import datetime

class APIResponse(BaseModel):
    statusCode: int
    data: Any | None = None
    message: str
    timestamp: datetime
    path: str
    error: Any | None = None