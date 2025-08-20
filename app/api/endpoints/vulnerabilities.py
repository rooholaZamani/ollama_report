from fastapi import APIRouter, HTTPException, Query
from app.services.report_generator import ReportGenerator
from app.models.report import Report
from typing import List, Optional
from pydantic import BaseModel
import httpx

# --- Pydantic Models for Vulnerability Data ---
class VulnerabilityStats(BaseModel):
    critical: int = 0
    high: int = 0
    criticalInProgress: int = 0
    fixRate: float = 0.0

class Vulnerability(BaseModel):
    title: str
    severity: str
    status: str
    organizationName: str
    discoveredDate: Optional[str] = None

# --- Router Definition ---
router = APIRouter(
    prefix="/vulnerabilities",
    tags=["Vulnerabilities Report"]
)
report_generator = ReportGenerator()
BACKEND_BASE_URL = "http://backend-reports:8080/api"

@router.post("/report", response_model=Report)
async def generate_vulnerability_report(
    model: str = "phi3:mini",
    limit: int = Query(5, description="تعداد آسیب‌پذیری‌های مهم برای نمایش در گزارش")
) -> Report:
    """تولید گزارش تحلیلی از آسیب‌پذیری‌های امنیتی"""

    try:
        async with httpx.AsyncClient() as client:
            # Fetch vulnerability statistics
            stats_response = await client.get(f"{BACKEND_BASE_URL}/vulnerabilities/stats")
            stats_response.raise_for_status()
            stats = VulnerabilityStats(**stats_response.json())

            # Fetch recent critical vulnerabilities
            vulns_response = await client.get(f"{BACKEND_BASE_URL}/vulnerabilities/severity/CRITICAL")
            vulns_response.raise_for_status()
            vulns_data = vulns_response.json()
            vulnerabilities = [Vulnerability(**vuln) for vuln in vulns_data[:limit]]

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to backend service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from backend: {e}")

    # Prepare details of important vulnerabilities for the prompt
    vulnerability_details = ""
    for i, vuln in enumerate(vulnerabilities):
        vulnerability_details += (
            f"- **آسیب‌پذیری {i+1}:**\n"
            f"  - **عنوان:** {vuln.title}\n"
            f"  - **شدت:** {vuln.severity}\n"
            f"  - **وضعیت:** {vuln.status}\n"
            f"  - **سازمان:** {vuln.organizationName}\n"
            f"  - **تاریخ شناسایی:** {vuln.discoveredDate or 'نامشخص'}\n\n"
        )
    
    prompt = f"""
    شما یک متخصص ارشد امنیت سایبری هستید. لطفاً بر اساس داده‌های زیر، یک گزارش تحلیلی در مورد وضعیت آسیب‌پذیری‌های سازمان به زبان فارسی تهیه کنید:

    **آمار کلی آسیب‌پذیری‌ها:**
    - تعداد آسیب‌پذیری‌های بحرانی (Critical): {stats.critical}
    - تعداد آسیب‌پذیری‌های با ریسک بالا (High): {stats.high}
    - تعداد آسیب‌پذیری‌های بحرانی در حال رفع: {stats.criticalInProgress}
    - نرخ رفع آسیب‌پذیری‌ها (Fix Rate): {stats.fixRate:.2f}%

    **جزئیات آسیب‌پذیری‌های بحرانی اخیر:**
    {vulnerability_details if vulnerability_details else "موردی یافت نشد."}

    **تحلیل و توصیه‌ها:**
    گزارش شما باید شامل موارد زیر باشد:
    1.  **وضعیت کلی:** ارزیابی کلی از وضعیت آسیب‌پذیری‌ها.
    2.  **تحلیل روند:** آیا در نوع یا شدت آسیب‌پذیری‌ها الگوی خاصی وجود دارد؟
    3.  **حوزه‌های پرخطر:** کدام سیستم‌ها یا سازمان‌ها بیشترین آسیب‌پذیری را دارند؟
    4.  **توصیه‌های عملی:** چه اقداماتی باید برای مدیریت و رفع این آسیب‌پذیری‌ها انجام شود؟ (با اولویت‌بندی)
    """

    try:
        return await report_generator.generate_report(model, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))