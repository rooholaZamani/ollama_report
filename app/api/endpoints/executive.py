from fastapi import APIRouter, HTTPException, Query
from app.services.report_generator import ReportGenerator
from app.models.report import Report
from typing import Optional
from pydantic import BaseModel
import httpx
from datetime import datetime, timedelta

# --- Models ---
class DashboardStats(BaseModel):
    totalOrganizations: int = 0
    totalActivities: int = 0
    completedActivities: int = 0
    pendingActivities: int = 0
    totalVulnerabilities: int = 0
    criticalVulnerabilities: int = 0
    totalIncidents: int = 0
    totalAssessments: int = 0

class OrganizationStat(BaseModel):
    name: str
    infrastructureType: str
    totalVulnerabilities: int = 0
    totalIncidents: int = 0
    riskLevel: str = "متوسط"

# --- Router Definition ---
router = APIRouter(
    prefix="/executive",
    tags=["Executive Reports"]
)
report_generator = ReportGenerator()
BACKEND_BASE_URL = "http://192.168.1.50:8080/api"

@router.post("/governor", response_model=Report)
async def generate_governor_report(
    model: str = "phi3:mini",
    quarter: Optional[int] = None,
    year: Optional[int] = None
) -> Report:
    """تولید گزارش سه‌ماهه برای استاندار"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get dashboard stats
            stats_response = await client.get(f"{BACKEND_BASE_URL}/dashboard/stats")
            stats_response.raise_for_status()
            stats = DashboardStats(**stats_response.json())

            # Get organization stats
            org_response = await client.get(f"{BACKEND_BASE_URL}/organizations/stats")
            org_response.raise_for_status()
            org_stats = org_response.json()

            # Get monthly summary
            monthly_response = await client.get(f"{BACKEND_BASE_URL}/reports/monthly-summary")
            monthly_response.raise_for_status()
            monthly_data = monthly_response.json()

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to backend service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from backend: {e}")

    current_quarter = quarter or ((datetime.now().month - 1) // 3 + 1)
    current_year = year or datetime.now().year

    prompt = f"""
    بسم الله الرحمن الرحیم

    شما مشاور ارشد امنیت سایبری استان هستید. یک گزارش اجرایی سه‌ماهه برای استاندار محترم تهیه کنید.

    **دوره گزارش:** فصل {current_quarter} سال {current_year}

    **آمار کلی استان:**
    - تعداد سازمان‌های تحت پوشش: {stats.totalOrganizations}
    - مجموع فعالیت‌های امنیتی: {stats.totalActivities}
    - فعالیت‌های تکمیل شده: {stats.completedActivities}
    - آسیب‌پذیری‌های شناسایی شده: {stats.totalVulnerabilities}
    - آسیب‌پذیری‌های بحرانی: {stats.criticalVulnerabilities}
    - رخدادهای امنیتی: {stats.totalIncidents}
    - ارزیابی‌های انجام شده: {stats.totalAssessments}

    **وضعیت سازمان‌های کلیدی:**
    {chr(10).join([f"- {org['name']}: {org.get('totalVulnerabilities', 0)} آسیب‌پذیری، {org.get('totalIncidents', 0)} رخداد" for org in org_stats[:5]])}

    **نکات مورد انتظار در گزارش:**
    1. **خلاصه اجرایی:** وضعیت کلی امنیت سایبری استان در یک پاراگراف
    2. **دستاوردهای کلیدی:** مهم‌ترین اقدامات و دستاوردهای سه ماه گذشته (3 مورد)
    3. **چالش‌های اساسی:** مهم‌ترین چالش‌ها و تهدیدات (2 مورد)
    4. **پیشنهادات راهبردی:** اقدامات پیشنهادی برای بهبود وضعیت (3 مورد)
    5. **نیازمندی‌های حمایتی:** موارد نیازمند حمایت و پیگیری استاندار محترم

    گزارش باید رسمی، مختصر و قابل ارائه در جلسه شورای امنیت استان باشد.
    از عبارات تخصصی پیچیده پرهیز کنید و بر نتایج کاربردی تمرکز کنید.
    """

    try:
        return await report_generator.generate_report(model, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/director-general", response_model=Report)
async def generate_director_general_report(
    model: str = "phi3:mini",
    month: Optional[int] = None,
    year: Optional[int] = None
) -> Report:
    """تولید گزارش ماهانه برای مدیرکل"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get dashboard stats
            stats_response = await client.get(f"{BACKEND_BASE_URL}/dashboard/stats")
            stats_response.raise_for_status()
            stats = DashboardStats(**stats_response.json())

            # Get user performance stats
            user_response = await client.get(f"{BACKEND_BASE_URL}/activities/user-stats")
            user_response.raise_for_status()
            user_stats = user_response.json()

            # Get vulnerability stats
            vuln_response = await client.get(f"{BACKEND_BASE_URL}/vulnerabilities/stats")
            vuln_response.raise_for_status()
            vuln_stats = vuln_response.json()

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to backend service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from backend: {e}")

    current_month = month or datetime.now().month
    current_year = year or datetime.now().year
    persian_months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                     "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]

    prompt = f"""
    شما رئیس مرکز امنیت سایبری استان هستید. یک گزارش ماهانه جامع برای مدیرکل محترم تهیه کنید.

    **دوره گزارش:** {persian_months[current_month-1]} {current_year}

    **آمار عملیاتی ماه جاری:**
    - مجموع فعالیت‌های انجام شده: {stats.totalActivities}
    - فعالیت‌های تکمیل شده: {stats.completedActivities}
    - فعالیت‌های در حال انجام: {stats.pendingActivities}
    - آسیب‌پذیری‌های کشف شده: {stats.totalVulnerabilities}
    - رخدادهای رسیدگی شده: {stats.totalIncidents}

    **عملکرد تیم‌ها:**
    تعداد کارشناسان فعال: {len(user_stats)}
    میانگین فعالیت هر کارشناس: {stats.totalActivities // max(len(user_stats), 1)}

    **آسیب‌پذیری‌ها:**
    - بحرانی: {vuln_stats.get('critical', 0)}
    - بالا: {vuln_stats.get('high', 0)}
    - متوسط: {vuln_stats.get('medium', 0)}
    - پایین: {vuln_stats.get('low', 0)}

    **ساختار گزارش:**
    1. **خلاصه عملکرد:** بررسی کلی فعالیت‌های ماه
    2. **شاخص‌های کلیدی عملکرد (KPI):**
       - نرخ تکمیل فعالیت‌ها
       - زمان پاسخ به رخدادها
       - پوشش ارزیابی سازمان‌ها
    3. **اقدامات شاخص:** مهم‌ترین اقدامات انجام شده
    4. **برنامه ماه آینده:** اولویت‌ها و برنامه‌های پیش رو
    5. **موانع و محدودیت‌ها:** مشکلات نیازمند رفع

    گزارش باید دقیق، مستند و قابل پیگیری باشد.
    از آمار و ارقام دقیق استفاده کنید.
    """

    try:
        return await report_generator.generate_report(model, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/center-director", response_model=Report)
async def generate_center_director_report(
    model: str = "phi3:mini"
) -> Report:
    """تولید گزارش جامع برای رئیس مرکز"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get comprehensive data
            stats_response = await client.get(f"{BACKEND_BASE_URL}/dashboard/stats")
            stats_response.raise_for_status()
            stats = DashboardStats(**stats_response.json())

            # Get all processes status
            process_response = await client.get(f"{BACKEND_BASE_URL}/processes")
            process_response.raise_for_status()
            processes = process_response.json()

            # Get recent activities
            activity_response = await client.get(f"{BACKEND_BASE_URL}/activities/recent?limit=10")
            activity_response.raise_for_status()
            recent_activities = activity_response.json()

            # Get organization details
            org_response = await client.get(f"{BACKEND_BASE_URL}/organizations")
            org_response.raise_for_status()
            organizations = org_response.json()

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to backend service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from backend: {e}")

    # Process breakdown
    process_summary = {}
    for proc in processes[:10]:
        process_summary[proc.get('typePersianName', proc.get('name', 'نامشخص'))] = proc.get('totalActivities', 0)

    prompt = f"""
    شما رئیس مرکز امنیت سایبری استان هستید. یک گزارش جامع و کامل از وضعیت فعلی و اقدامات در دست انجام تهیه کنید.

    **تاریخ گزارش:** {datetime.now().strftime('%Y/%m/%d')}

    **وضعیت کلی مرکز:**
    - سازمان‌های تحت پوشش: {stats.totalOrganizations}
    - کل فعالیت‌های ثبت شده: {stats.totalActivities}
    - فعالیت‌های تکمیل شده: {stats.completedActivities}
    - فعالیت‌های در حال انجام: {stats.pendingActivities}

    **وضعیت فرآیندهای 10‌گانه:**
    {chr(10).join([f"- {name}: {count} فعالیت" for name, count in process_summary.items()])}

    **آسیب‌پذیری‌ها و رخدادها:**
    - کل آسیب‌پذیری‌ها: {stats.totalVulnerabilities}
    - آسیب‌پذیری‌های بحرانی رفع نشده: {stats.criticalVulnerabilities}
    - رخدادهای جاری: {stats.totalIncidents}

    **سازمان‌های دارای اولویت:**
    - تعداد سازمان‌های IT: {len([o for o in organizations if o.get('infrastructureType') == 'IT'])}
    - تعداد سازمان‌های OT: {len([o for o in organizations if o.get('infrastructureType') == 'OT'])}
    - تعداد سازمان‌های Hybrid: {len([o for o in organizations if o.get('infrastructureType') == 'Hybrid'])}

    **فعالیت‌های اخیر:** {len(recent_activities)} فعالیت در هفته گذشته

    **ساختار گزارش مورد نیاز:**

    1. **وضعیت عملیاتی مرکز:**
       - آمادگی عملیاتی تیم‌ها
       - پوشش 24/7 مرکز SOC
       - وضعیت سیستم‌های پایش

    2. **اقدامات در دست انجام:**
       - پروژه‌های جاری (با درصد پیشرفت)
       - ارزیابی‌های در حال انجام
       - رخدادهای در حال پیگیری

    3. **تحلیل وضعیت امنیتی استان:**
       - سطح تهدید فعلی
       - آسیب‌پذیری‌های اولویت‌دار
       - پیش‌بینی تهدیدات آینده

    4. **عملکرد تیم‌های تخصصی:**
       - تیم رسیدگی به رخداد
       - تیم ارزیابی و ممیزی
       - تیم شکار تهدید
       - تیم آموزش

    5. **هماهنگی‌های بین‌سازمانی:**
       - جلسات برگزار شده
       - تفاهم‌نامه‌های منعقد شده
       - همکاری با مرکز ماهر

    6. **برنامه‌ریزی آینده:**
       - اولویت‌های هفته آینده
       - برنامه‌های ماه آینده
       - نیازمندی‌های فوری

    7. **چالش‌ها و راهکارها:**
       - مشکلات فنی
       - کمبود منابع
       - راهکارهای پیشنهادی

    گزارش باید بسیار دقیق، جامع و عملیاتی باشد.
    تمام جزئیات مهم را پوشش دهید.
    از جداول و لیست‌ها برای وضوح بیشتر استفاده کنید.
    """

    try:
        return await report_generator.generate_report(model, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))