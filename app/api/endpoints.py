"""
API endpoints definition.
"""
from fastapi import APIRouter, HTTPException
from app.services.report_generator import ReportGenerator
from app.models.report import Report
from typing import Dict, Any, List
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
        ChecklistItem(id=1, description="آیا فایروال به درستی پیکربندی شده است؟", completed=False),
        ChecklistItem(id=2, description="آیا پسوردهای قوی برای تمام اکانت ها استفاده شده؟", completed=False),
        ChecklistItem(id=3, description="آیا تمام نرم افزارها به روزرسانی شده اند؟", completed=False),
        ChecklistItem(id=4, description="آیا SSL/TLS فعال است؟", completed=False),
        ChecklistItem(id=5, description="آیا backup منظم انجام می شود؟", completed=False),
        ChecklistItem(id=6, description="آیا سطح دسترسی کاربران محدود شده؟", completed=False),
        ChecklistItem(id=7, description="آیا monitoring و logging فعال است؟", completed=False),
        ChecklistItem(id=8, description="آیا VPN برای دسترسی راه دور استفاده می شود؟", completed=False),
        ChecklistItem(id=9, description="آیا antivirus نصب و فعال است؟", completed=False),
        ChecklistItem(id=10, description="آیا پورت های غیرضروری بسته شده اند؟", completed=False)
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



@router.post("/checklist/report-simple", response_model=Report)
async def generate_simple_checklist_report(completed_status: List[bool], model: str = "phi3:mini") -> Report:
    """تولید گزارش بر اساس وضعیت آیتم های چک لیست (فقط true/false ها)"""
    
    # چک لیست پیش فرض (همون که قبلاً ساختیم)
    security_descriptions = [
        "آیا فایروال به درستی پیکربندی شده است؟",
        "آیا پسوردهای قوی برای تمام اکانت ها استفاده شده؟",
        "آیا تمام نرم افزارها به روزرسانی شده اند؟",
        "آیا SSL/TLS فعال است؟",
        "آیا backup منظم انجام می شود؟",
        "آیا سطح دسترسی کاربران محدود شده؟",
        "آیا monitoring و logging فعال است؟",
        "آیا VPN برای دسترسی راه دور استفاده می شود؟",
        "آیا antivirus نصب و فعال است؟",
        "آیا پورت های غیرضروری بسته شده اند؟"
    ]
    
    # تطبیق وضعیت با توضیحات
    completed_items = [desc for i, desc in enumerate(security_descriptions) if i < len(completed_status) and completed_status[i]]
    incomplete_items = [desc for i, desc in enumerate(security_descriptions) if i < len(completed_status) and not completed_status[i]]
    
    prompt = f"""
    بر اساس چک لیست امنیت شبکه، یک گزارش کامل امنیتی به زبان فارسی تهیه کن:

    ✅ موارد انجام شده ({len(completed_items)} مورد):
    {chr(10).join([f"- {item}" for item in completed_items])}

    ❌ موارد انجام نشده ({len(incomplete_items)} مورد):
    {chr(10).join([f"- {item}" for item in incomplete_items])}

    لطفاً گزارش شامل موارد زیر باشد:
    1. خلاصه وضعیت امنیتی فعلی
    2. نقاط قوت (موارد انجام شده)
    3. نقاط ضعف و خطرات (موارد انجام نشده)
    4. اولویت‌بندی موارد انجام نشده
    5. توصیه‌های عملی برای بهبود امنیت
    6. نتیجه‌گیری و درجه امنیت کلی (از 10)

    گزارش باید حرفه‌ای و قابل ارائه به مدیریت باشد.
    """
    
    try:
        return await report_generator.generate_report(model, prompt)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Ollama service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))