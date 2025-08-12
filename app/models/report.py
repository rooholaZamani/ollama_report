"""
Report model definition.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Report(BaseModel):
    title: str
    content: str
    generated_at: Optional[datetime] = None
    model_used: str
    metadata: Optional[dict] = None
    
    def __init__(self, **data):
        if 'generated_at' not in data:
            data['generated_at'] = datetime.now()
        super().__init__(**data)