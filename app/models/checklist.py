"""
Checklist model definition.
"""
from pydantic import BaseModel
from typing import List

class ChecklistItem(BaseModel):
    description: str
    completed: bool = False

class Checklist(BaseModel):
    title: str
    items: List[ChecklistItem]
