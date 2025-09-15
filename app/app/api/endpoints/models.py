from fastapi import APIRouter, HTTPException
from app.services.report_generator import ReportGenerator
from app.models.report import Report
from typing import Dict, Any
import httpx

router = APIRouter(
    tags=["Ollama Models"]
)
report_generator = ReportGenerator()

@router.get("/models", response_model=Dict[str, Any])
async def list_models() -> Dict[str, Any]:
    """
    List available Ollama models.
    """
    try:
        return await report_generator.ollama_client.list_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=Report)
async def generate_report(model: str, prompt: str) -> Report:
    """
    Generate a report using the specified model and prompt (generic endpoint).
    """
    if not model or not prompt:
        raise HTTPException(status_code=400, detail="Model and prompt are required")
    
    try:
        return await report_generator.generate_report(model, prompt)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Ollama service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))