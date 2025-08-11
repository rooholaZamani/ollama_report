"""
API endpoints definition.
"""
from fastapi import APIRouter, HTTPException
from app.services.report_generator import ReportGenerator
from app.models.report import Report
from typing import Dict, Any

router = APIRouter()
report_generator = ReportGenerator()

@router.post("/generate", response_model=Report)
async def generate_report(model: str, prompt: str) -> Report:
    """
    Generate a report using the specified model and prompt.
    """
    try:
        return await report_generator.generate_report(model, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """
    List available Ollama models.
    """
    try:
        return await report_generator.ollama_client.list_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
