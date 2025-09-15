from fastapi import APIRouter, HTTPException, Query
from app.services.report_generator import ReportGenerator
from app.models.report import Report
from typing import List, Optional
from pydantic import BaseModel
import httpx

# --- Models can be in a shared file, but for simplicity are here ---
class IncidentStats(BaseModel):
    totalIncidents: int = 0
    criticalIncidents: int = 0
    highSeverityIncidents: int = 0
    investigatingIncidents: int = 0
    averageResolutionTime: float = 0.0

class Incident(BaseModel):
    title: str
    severity: str
    status: str
    organizationName: str
    detectionDate: Optional[str] = None

# --- Router Definition ---
router = APIRouter(
    prefix="/incidents",
    tags=["Incidents Report"]
)
report_generator = ReportGenerator()
BACKEND_BASE_URL = "http://192.168.1.50:8080/api"

@router.post("/report", response_model=Report)
async def generate_incident_report(
    model: str = "phi3:mini",
    limit: int = Query(5, description="تعداد رخدادهای مهم برای نمایش در گزارش")
) -> Report:
    """تولید گزارش تحلیلی از رخدادهای امنیتی"""
    # ... (کد کامل این تابع که قبلاً نوشته شده بود)
    try:
        async with httpx.AsyncClient() as client:
            stats_response = await client.get(f"{BACKEND_BASE_URL}/incidents/stats")
            stats_response.raise_for_status()
            stats = IncidentStats(**stats_response.json())

            incidents_response = await client.get(f"{BACKEND_BASE_URL}/incidents/critical")
            incidents_response.raise_for_status()
            incidents_data = incidents_response.json()
            incidents = [Incident(**inc) for inc in incidents_data[:limit]]

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to backend service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from backend: {e}")

    incident_details = ""
    for i, incident in enumerate(incidents):
        incident_details += (f"- **رخداد {i+1}:**\n  - **عنوان:** {incident.title}\n  - **شدت:** {incident.severity}\n  - **وضعیت:** {incident.status}\n  - **سازمان:** {incident.organizationName}\n  - **تاریخ شناسایی:** {incident.detectionDate or 'نامشخص'}\n\n")

    prompt = f"""
    شما یک تحلیلگر ارشد امنیت سایبری هستید. بر اساس داده‌های زیر، یک گزارش مدیریتی جامع در مورد وضعیت رخدادهای امنیتی به زبان فارسی تهیه کنید:
    **آمار کلی رخدادها:**
    - کل رخدادها: {stats.totalIncidents}
    - رخدادهای بحرانی: {stats.criticalIncidents}
    - رخدادهای با شدت بالا: {stats.highSeverityIncidents}
    - رخدادهای در حال بررسی: {stats.investigatingIncidents}
    - میانگین زمان رفع رخدادها (ساعت): {stats.averageResolutionTime:.2f}
    **جزئیات رخدادهای بحرانی اخیر:**
    {incident_details if incident_details else "موردی یافت نشد."}
    **تحلیل و پیشنهادات:**
    گزارش شما باید شامل موارد زیر باشد:
    1.  **خلاصه اجرایی:** وضعیت کلی رخدادها در یک پاراگراف.
    2.  **تحلیل روندها:** آیا روند خاصی در نوع یا شدت رخدادها مشاهده می‌شود؟
    3.  **ریسک‌های اصلی:** مهم‌ترین ریسک‌هایی که سازمان با آن مواجه است کدامند؟
    4.  **پیشنهادات کلیدی:** چه اقداماتی برای بهبود وضعیت پیشنهاد می‌کنید؟ (اولویت‌بندی شده)
    """
    
    try:
        return await report_generator.generate_report(model, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))