"""
Report model definition.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Report(BaseModel):
    title: str
    content: str
    generated_at: datetime = datetime.now()
    model_used: str
    metadata: Optional[dict] = None
