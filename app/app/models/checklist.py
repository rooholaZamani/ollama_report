"""
Checklist model definition for cybersecurity processes.
"""
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime

class ProcessType(str, Enum):
    FIELD_ASSESSMENT = "FIELD_ASSESSMENT"
    SECURITY_PLAN_MONITORING = "SECURITY_PLAN_MONITORING"
    THREAT_MONITORING = "THREAT_MONITORING"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"
    FORENSICS = "FORENSICS"
    THREAT_HUNTING = "THREAT_HUNTING"
    CYBER_SECURITY_GUIDANCE = "CYBER_SECURITY_GUIDANCE"
    CONSULTANT_CERTIFICATION = "CONSULTANT_CERTIFICATION"
    TRAINING = "TRAINING"
    CYBER_EXERCISE = "CYBER_EXERCISE"

class ChecklistItem(BaseModel):
    id: Optional[int] = None
    description: str
    completed: bool = False
    priority: str = "medium"  # low, medium, high, critical
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None

class Checklist(BaseModel):
    id: Optional[int] = None
    title: str
    process_type: ProcessType
    organization_id: Optional[int] = None
    items: List[ChecklistItem]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completion_percentage: Optional[float] = 0.0

class CreateChecklistRequest(BaseModel):
    title: str
    process_type: ProcessType
    organization_id: Optional[int] = None
    items: List[ChecklistItem] = []

class UpdateChecklistRequest(BaseModel):
    title: Optional[str] = None
    items: Optional[List[ChecklistItem]] = None
