"""
Checklist management endpoints for cybersecurity processes.
"""
from fastapi import APIRouter, HTTPException
from app.models.checklist import (
    Checklist,
    CreateChecklistRequest,
    UpdateChecklistRequest,
    ProcessType
)
from app.services.report_generator import ReportGenerator
from typing import List, Dict, Any
import httpx
from datetime import datetime

router = APIRouter(
    prefix="/checklists",
    tags=["Checklists"]
)

# In-memory storage for demo (in production, use database)
checklists_db: Dict[int, Checklist] = {}
next_id = 1

report_generator = ReportGenerator()

@router.get("/", response_model=List[Checklist])
async def get_all_checklists() -> List[Checklist]:
    """
    Retrieve all checklists.
    """
    return list(checklists_db.values())

@router.get("/{checklist_id}", response_model=Checklist)
async def get_checklist(checklist_id: int) -> Checklist:
    """
    Retrieve a specific checklist by ID.
    """
    if checklist_id not in checklists_db:
        raise HTTPException(status_code=404, detail="Checklist not found")

    return checklists_db[checklist_id]

@router.post("/", response_model=Checklist)
async def create_checklist(request: CreateChecklistRequest) -> Checklist:
    """
    Create a new cybersecurity process checklist.
    """
    global next_id

    checklist = Checklist(
        id=next_id,
        title=request.title,
        process_type=request.process_type,
        organization_id=request.organization_id,
        items=request.items,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        completion_percentage=0.0
    )

    checklists_db[next_id] = checklist
    next_id += 1

    return checklist

@router.put("/{checklist_id}", response_model=Checklist)
async def update_checklist(checklist_id: int, request: UpdateChecklistRequest) -> Checklist:
    """
    Update an existing checklist.
    """
    if checklist_id not in checklists_db:
        raise HTTPException(status_code=404, detail="Checklist not found")

    checklist = checklists_db[checklist_id]

    if request.title is not None:
        checklist.title = request.title

    if request.items is not None:
        checklist.items = request.items
        # Recalculate completion percentage
        if checklist.items:
            completed_items = sum(1 for item in checklist.items if item.completed)
            checklist.completion_percentage = (completed_items / len(checklist.items)) * 100
        else:
            checklist.completion_percentage = 0.0

    checklist.updated_at = datetime.now()

    return checklist

@router.delete("/{checklist_id}")
async def delete_checklist(checklist_id: int) -> Dict[str, str]:
    """
    Delete a checklist.
    """
    if checklist_id not in checklists_db:
        raise HTTPException(status_code=404, detail="Checklist not found")

    del checklists_db[checklist_id]
    return {"message": "Checklist deleted successfully"}

@router.get("/by-process/{process_type}", response_model=List[Checklist])
async def get_checklists_by_process(process_type: ProcessType) -> List[Checklist]:
    """
    Retrieve checklists by process type.
    """
    return [checklist for checklist in checklists_db.values()
            if checklist.process_type == process_type]

@router.post("/{checklist_id}/generate-report")
async def generate_checklist_report(checklist_id: int, model: str = "llama3.2") -> Dict[str, Any]:
    """
    Generate an AI-powered report for a checklist using Ollama.
    """
    if checklist_id not in checklists_db:
        raise HTTPException(status_code=404, detail="Checklist not found")

    checklist = checklists_db[checklist_id]

    # Create a detailed prompt for the checklist report
    completed_items = [item for item in checklist.items if item.completed]
    pending_items = [item for item in checklist.items if not item.completed]

    prompt = f"""
    Generate a comprehensive cybersecurity checklist report for the following:

    Checklist Title: {checklist.title}
    Process Type: {checklist.process_type.value}
    Completion Rate: {checklist.completion_percentage:.1f}%

    Completed Items ({len(completed_items)}):
    {chr(10).join([f"✓ {item.description}" for item in completed_items])}

    Pending Items ({len(pending_items)}):
    {chr(10).join([f"○ {item.description}" for item in pending_items])}

    Please provide:
    1. Executive Summary
    2. Compliance Status Analysis
    3. Risk Assessment of pending items
    4. Recommendations for improvement
    5. Next steps and timeline

    Format the report professionally for cybersecurity stakeholders.
    """

    try:
        report = await report_generator.generate_report(model, prompt)
        return {
            "checklist_id": checklist_id,
            "report": report,
            "generated_at": datetime.now().isoformat()
        }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Ollama service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{process_type}")
async def get_checklist_template(process_type: ProcessType) -> Dict[str, Any]:
    """
    Get a template checklist for a specific cybersecurity process type.
    """
    templates = {
        ProcessType.FIELD_ASSESSMENT: {
            "title": f"Field Security Assessment Checklist",
            "items": [
                {"description": "Review physical security perimeter", "priority": "high"},
                {"description": "Assess access control systems", "priority": "high"},
                {"description": "Evaluate network security architecture", "priority": "critical"},
                {"description": "Check security policies and procedures", "priority": "medium"},
                {"description": "Verify employee security awareness", "priority": "medium"},
                {"description": "Test incident response procedures", "priority": "high"},
                {"description": "Review security logs and monitoring", "priority": "high"}
            ]
        },
        ProcessType.INCIDENT_RESPONSE: {
            "title": "Incident Response Checklist",
            "items": [
                {"description": "Identify and classify incident", "priority": "critical"},
                {"description": "Isolate affected systems", "priority": "critical"},
                {"description": "Preserve evidence", "priority": "high"},
                {"description": "Notify stakeholders", "priority": "high"},
                {"description": "Document incident timeline", "priority": "medium"},
                {"description": "Implement containment measures", "priority": "critical"},
                {"description": "Conduct post-incident review", "priority": "medium"}
            ]
        },
        ProcessType.THREAT_HUNTING: {
            "title": "Threat Hunting Process Checklist",
            "items": [
                {"description": "Define hunting hypothesis", "priority": "high"},
                {"description": "Collect and analyze threat intelligence", "priority": "high"},
                {"description": "Review network traffic patterns", "priority": "medium"},
                {"description": "Analyze system logs for anomalies", "priority": "high"},
                {"description": "Check for indicators of compromise", "priority": "critical"},
                {"description": "Validate findings", "priority": "high"},
                {"description": "Update detection rules", "priority": "medium"}
            ]
        }
    }

    if process_type not in templates:
        # Generic template for other process types
        return {
            "title": f"{process_type.value.replace('_', ' ').title()} Checklist",
            "items": [
                {"description": "Define process objectives", "priority": "medium"},
                {"description": "Assign responsibilities", "priority": "medium"},
                {"description": "Execute process steps", "priority": "high"},
                {"description": "Monitor progress", "priority": "medium"},
                {"description": "Document results", "priority": "medium"},
                {"description": "Review and improve", "priority": "low"}
            ]
        }

    return templates[process_type]