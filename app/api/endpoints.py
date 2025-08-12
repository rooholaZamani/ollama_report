"""
API endpoints definition.
"""
from fastapi import APIRouter, HTTPException
from app.services.report_generator import ReportGenerator
from app.models.report import Report
from typing import Dict, Any
from app.models.checklist import Checklist, ChecklistItem
import httpx

router = APIRouter()
report_generator = ReportGenerator()

@router.post("/generate", response_model=Report)
async def generate_report(model: str, prompt: str) -> Report:
    """Generate a report using the specified model and prompt."""
    if not model or not prompt:
        raise HTTPException(status_code=400, detail="Model and prompt are required")
    
    try:
        return await report_generator.generate_report(model, prompt)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Ollama service unavailable: {str(e)}")
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

    
@router.get("/checklist", response_model=Checklist)
async def get_security_checklist() -> Checklist:
    """دریافت چک لیست امنیت شبکه"""
    security_items = [
        ChecklistItem(description="آیا فایروال به درستی پیکربندی شده است؟", completed=False),
        ChecklistItem(description="آیا پسوردهای قوی برای تمام اکانت ها استفاده شده؟", completed=False),
        ChecklistItem(description="آیا تمام نرم افزارها به روزرسانی شده اند؟", completed=False),
        ChecklistItem(description="آیا SSL/TLS فعال است؟", completed=False),
        ChecklistItem(description="آیا backup منظم انجام می شود؟", completed=False),
        ChecklistItem(description="آیا سطح دسترسی کاربران محدود شده؟", completed=False),
        ChecklistItem(description="آیا monitoring و logging فعال است؟", completed=False),
        ChecklistItem(description="آیا VPN برای دسترسی راه دور استفاده می شود؟", completed=False),
        ChecklistItem(description="آیا antivirus نصب و فعال است؟", completed=False),
        ChecklistItem(description="آیا پورت های غیرضروری بسته شده اند؟", completed=False)
    ]
    
    return Checklist(title="چک لیست امنیت شبکه", items=security_items)

@router.put("/checklist/item/{item_index}", response_model=dict)
async def update_checklist_item(item_index: int, completed: bool) -> dict:
    """به روزرسانی وضعیت یک آیتم چک لیست"""
    # در اینجا می‌تونی منطق ذخیره سازی رو اضافه کنی
    return {"message": f"آیتم {item_index} به وضعیت {completed} تغییر کرد", "item_index": item_index, "completed": completed}

@router.post("/checklist", response_model=Checklist)
async def create_custom_checklist(checklist: Checklist) -> Checklist:
    """ایجاد چک لیست سفارشی"""
    return checklist
