from fastapi import APIRouter, HTTPException, Query
from app.services.report_generator import ReportGenerator
from app.models.report import Report
from typing import List, Optional
from pydantic import BaseModel
import httpx

# --- Pydantic Models for Assessment Data ---
class AssessmentStats(BaseModel):
    totalAssessments: int = 0
    completedAssessments: int = 0
    inProgressAssessments: int = 0
    averageRiskScore: float = 0.0
    completionRate: float = 0.0

class Assessment(BaseModel):
    title: str
    organizationName: str
    status: str
    riskScore: Optional[int] = None
    assessmentDate: Optional[str] = None
    riskLevel: Optional[str] = None

# --- Router Definition ---
router = APIRouter(
    prefix="/assessments",
    tags=["Assessments Report"]
)
report_generator = ReportGenerator()
BACKEND_BASE_URL = "http://192.168.1.50:8080/api"

@router.post("/report", response_model=Report)
async def generate_assessment_report(
    model: str = "phi3:mini",
    limit: int = Query(5, description="تعداد ممیزی‌های اخیر برای نمایش در گزارش")
) -> Report:
    """تولید گزارش تحلیلی از ممیزی‌ها و ارزیابی‌های امنیتی"""

    try:
        async with httpx.AsyncClient() as client:
            # Fetch assessment statistics
            stats_response = await client.get(f"{BACKEND_BASE_URL}/assessments/stats")
            stats_response.raise_for_status()
            stats = AssessmentStats(**stats_response.json())

            # Fetch recent completed assessments
            assessments_response = await client.get(f"{BACKEND_BASE_URL}/assessments")
            assessments_response.raise_for_status()
            assessments_data = assessments_response.json()
            
            # Filter for completed assessments and sort by date to get the most recent ones
            completed_assessments = sorted(
                [a for a in assessments_data if a.get("status") == "COMPLETED"],
                key=lambda x: x.get("assessmentDate", ""),
                reverse=True
            )
            assessments = [Assessment(**asm) for asm in completed_assessments[:limit]]

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to backend service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from backend: {e}")

    # Prepare details of important assessments for the prompt
    assessment_details = ""
    for i, asm in enumerate(assessments):
        assessment_details += (
            f"- **ممیزی {i+1}:**\n"
            f"  - **عنوان:** {asm.title}\n"
            f"  - **سازمان:** {asm.organizationName}\n"
            f"  - **نمره ریسک:** {asm.riskScore or 'N/A'} (سطح: {asm.riskLevel or 'نامشخص'})\n"
            f"  - **تاریخ:** {asm.assessmentDate or 'نامشخص'}\n\n"
        )
    
    prompt = f"""
    شما یک مشاور ارشد امنیت و ممیزی سایبری هستید. بر اساس داده‌های زیر، یک گزارش مدیریتی جامع در مورد وضعیت ممیزی‌های امنیتی سازمان تهیه کنید:

    **آمار کلی ممیزی‌ها (Assessments):**
    - تعداد کل ممیزی‌ها: {stats.totalAssessments}
    - ممیزی‌های تکمیل‌شده: {stats.completedAssessments}
    - ممیزی‌های در حال انجام: {stats.inProgressAssessments}
    - میانگین نمره ریسک: {stats.averageRiskScore:.2f} از ۱۰۰
    - نرخ تکمیل ممیزی‌ها: {stats.completionRate:.2f}%

    **جزئیات آخرین ممیزی‌های تکمیل‌شده:**
    {assessment_details if assessment_details else "موردی یافت نشد."}

    **تحلیل و توصیه‌ها:**
    گزارش شما باید شامل موارد زیر باشد:
    1.  **خلاصه اجرایی:** ارزیابی کلی از وضعیت ممیزی‌ها و سطح ریسک سازمان.
    2.  **تحلیل روند:** آیا نمره ریسک سازمان در حال بهبود است یا خیر؟
    3.  **سازمان‌های پرخطر:** کدام سازمان‌ها بر اساس نمره ریسک، نیاز به توجه فوری دارند؟
    4.  **توصیه‌های راهبردی:** چه اقداماتی برای بهبود فرآیندهای ممیزی و کاهش ریسک کلی پیشنهاد می‌کنید؟
    """

    try:
        return await report_generator.generate_report(model, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))