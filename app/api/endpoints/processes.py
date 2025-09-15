from fastapi import APIRouter, HTTPException, Query, Path
from app.services.report_generator import ReportGenerator
from app.models.report import Report
from typing import Optional, List
from pydantic import BaseModel
import httpx
from datetime import datetime
from enum import Enum

# --- Process Types Enum ---
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
    INFRASTRUCTURE_MONITORING = "INFRASTRUCTURE_MONITORING"
    SECURITY_PLAN_STATUS = "SECURITY_PLAN_STATUS"
    COMPLIANCE_REQUIREMENTS = "COMPLIANCE_REQUIREMENTS"
    INCIDENT_TRACKING = "INCIDENT_TRACKING"
    THREAT_HUNTING_PREVENTION = "THREAT_HUNTING_PREVENTION"
    MONITORING_DEVELOPMENT = "MONITORING_DEVELOPMENT"
    INFRASTRUCTURE_GUIDANCE = "INFRASTRUCTURE_GUIDANCE"
    SPECIAL_ACTIONS = "SPECIAL_ACTIONS"

# --- Models ---
class ProcessActivity(BaseModel):
    title: str
    description: Optional[str] = None
    status: str
    organizationName: Optional[str] = None
    assignedTo: Optional[str] = None
    createdDate: Optional[str] = None
    completedDate: Optional[str] = None

class ProcessStats(BaseModel):
    processName: str
    totalActivities: int = 0
    completedActivities: int = 0
    pendingActivities: int = 0
    inProgressActivities: int = 0

# --- Router Definition ---
router = APIRouter(
    prefix="/processes",
    tags=["Process Reports"]
)
report_generator = ReportGenerator()
BACKEND_BASE_URL = "http://192.168.1.50:8080/api"

# --- Helper Functions ---
def get_process_persian_name(process_type: ProcessType) -> str:
    mapping = {
        ProcessType.FIELD_ASSESSMENT: "بررسی و ارزیابی میدانی",
        ProcessType.SECURITY_PLAN_MONITORING: "نظارت بر اجرای طرح‌های امنیتی",
        ProcessType.THREAT_MONITORING: "پایش و تحلیل تهدیدات (SOC)",
        ProcessType.INCIDENT_RESPONSE: "تیم رسیدگی به رخداد",
        ProcessType.FORENSICS: "فارنزیک",
        ProcessType.THREAT_HUNTING: "شکار تهدید",
        ProcessType.CYBER_SECURITY_GUIDANCE: "هدایت و راهبری امنیت سایبری",
        ProcessType.CONSULTANT_CERTIFICATION: "تعیین صلاحیت مشاوران",
        ProcessType.TRAINING: "آموزش",
        ProcessType.CYBER_EXERCISE: "مانور سایبری",
        ProcessType.INFRASTRUCTURE_MONITORING: "اشراف بر وضعیت زیرساخت‌ها",
        ProcessType.SECURITY_PLAN_STATUS: "وضعیت اجرای طرح امن‌سازی",
        ProcessType.COMPLIANCE_REQUIREMENTS: "وضعیت الزام اجرای الزامات",
        ProcessType.INCIDENT_TRACKING: "گزارش پیگیری رخدادها",
        ProcessType.THREAT_HUNTING_PREVENTION: "گزارش شکار تهدید و پیشگیری",
        ProcessType.MONITORING_DEVELOPMENT: "توسعه پایش",
        ProcessType.INFRASTRUCTURE_GUIDANCE: "هدایت و نظارت زیرساخت‌ها",
        ProcessType.SPECIAL_ACTIONS: "اقدامات ویژه"
    }
    return mapping.get(process_type, process_type.value)

# --- SOC Monitoring Report ---
@router.post("/soc-monitoring", response_model=Report)
async def generate_soc_monitoring_report(
    model: str = "phi3:mini",
    days: int = Query(7, description="تعداد روزهای گذشته برای تحلیل")
) -> Report:
    """تولید گزارش پایش و تحلیل تهدیدات SOC"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get SOC monitoring data
            response = await client.get(f"{BACKEND_BASE_URL}/activities/by-process/THREAT_MONITORING")
            response.raise_for_status()
            activities = response.json()

            # Get incident stats
            inc_response = await client.get(f"{BACKEND_BASE_URL}/incidents/stats")
            inc_response.raise_for_status()
            incident_stats = inc_response.json()

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to backend service: {e}")

    prompt = f"""
    شما تحلیلگر ارشد مرکز عملیات امنیت (SOC) هستید. گزارش جامع پایش و تحلیل تهدیدات را تهیه کنید.

    **دوره گزارش:** {days} روز گذشته

    **آمار پایش:**
    - تعداد کل هشدارهای دریافتی: {len(activities)}
    - رخدادهای شناسایی شده: {incident_stats.get('totalIncidents', 0)}
    - رخدادهای بحرانی: {incident_stats.get('criticalIncidents', 0)}

    **ساختار گزارش:**

    1. **خلاصه وضعیت SOC:**
       - وضعیت عملیاتی مرکز
       - پوشش 24/7
       - آمادگی تیم‌ها

    2. **تحلیل هشدارها:**
       - دسته‌بندی هشدارها بر اساس نوع تهدید
       - الگوهای مشکوک شناسایی شده
       - نرخ False Positive

    3. **تهدیدات شناسایی شده:**
       - بدافزارها و ransomware
       - حملات phishing
       - نفوذ و دسترسی غیرمجاز
       - حملات DDoS

    4. **شاخص‌های عملکردی (KPIs):**
       - میانگین زمان شناسایی (MTTD)
       - میانگین زمان پاسخ (MTTR)
       - نرخ موفقیت در مهار تهدیدات

    5. **تحلیل روند:**
       - مقایسه با دوره قبل
       - پیش‌بینی تهدیدات آینده
       - نقاط آسیب‌پذیر شناسایی شده

    6. **توصیه‌های امنیتی:**
       - اقدامات فوری
       - بهبود قوانین SIEM
       - نیاز به به‌روزرسانی‌ها

    از داده‌های واقعی و آمار دقیق استفاده کنید.
    بر تهدیدات فعال و در حال ظهور تمرکز کنید.
    """

    try:
        return await report_generator.generate_report(model, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Forensics Report ---
@router.post("/forensics", response_model=Report)
async def generate_forensics_report(
    model: str = "phi3:mini",
    case_id: Optional[int] = None
) -> Report:
    """تولید گزارش تحلیل فارنزیک"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get forensics activities
            response = await client.get(f"{BACKEND_BASE_URL}/activities/by-process/FORENSICS")
            response.raise_for_status()
            forensics_activities = response.json()

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to backend service: {e}")

    prompt = f"""
    شما کارشناس ارشد فارنزیک دیجیتال هستید. گزارش تحلیل فارنزیک را تهیه کنید.

    **تعداد پرونده‌های فارنزیک:** {len(forensics_activities)}

    **ساختار گزارش فارنزیک:**

    1. **خلاصه اجرایی:**
       - تعداد پرونده‌های بررسی شده
       - نوع رخدادهای تحلیل شده
       - نتایج کلیدی

    2. **روش‌شناسی تحلیل:**
       - ابزارهای استفاده شده
       - فرآیند جمع‌آوری شواهد
       - زنجیره حفاظت (Chain of Custody)

    3. **یافته‌های فنی:**
       - شواهد دیجیتال کشف شده
       - مسیر نفوذ و روش حمله
       - Indicators of Compromise (IoCs)
       - Timeline رخدادها

    4. **تحلیل بدافزار (در صورت وجود):**
       - نوع و خانواده بدافزار
       - رفتار و عملکرد
       - مکانیزم انتشار
       - اثرات و خسارات

    5. **بازیابی داده‌ها:**
       - داده‌های بازیابی شده
       - داده‌های از دست رفته
       - امکان بازیابی کامل

    6. **توصیه‌های امنیتی:**
       - اقدامات اصلاحی فوری
       - پیشگیری از رخدادهای مشابه
       - بهبود قابلیت‌های فارنزیک

    7. **مستندسازی قانونی:**
       - آماده‌سازی برای ارائه در مراجع قضایی
       - شواهد قابل استناد

    گزارش باید دقیق، فنی و قابل استناد در مراجع قانونی باشد.
    """

    try:
        return await report_generator.generate_report(model, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Threat Hunting Report ---
@router.post("/threat-hunting", response_model=Report)
async def generate_threat_hunting_report(
    model: str = "phi3:mini",
    focus_area: Optional[str] = None
) -> Report:
    """تولید گزارش شکار تهدید"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get threat hunting activities
            response = await client.get(f"{BACKEND_BASE_URL}/activities/by-process/THREAT_HUNTING")
            response.raise_for_status()
            hunting_activities = response.json()

            # Get vulnerability data for correlation
            vuln_response = await client.get(f"{BACKEND_BASE_URL}/vulnerabilities/stats")
            vuln_response.raise_for_status()
            vuln_stats = vuln_response.json()

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to backend service: {e}")

    prompt = f"""
    شما متخصص شکار تهدید پیشرفته هستید. گزارش جامع شکار تهدید را تهیه کنید.

    **فعالیت‌های شکار تهدید:** {len(hunting_activities)} عملیات

    **ساختار گزارش شکار تهدید:**

    1. **خلاصه عملیات شکار:**
       - تعداد عملیات‌های انجام شده
       - حوزه‌های تحت بررسی
       - تهدیدات کشف شده

    2. **روش‌ها و تکنیک‌ها:**
       - Hypothesis-driven hunting
       - IoC-based hunting
       - Behavioral analysis
       - MITRE ATT&CK mapping

    3. **تهدیدات شناسایی شده:**
       - APT groups فعال
       - تکنیک‌های نفوذ جدید
       - Lateral movement patterns
       - Data exfiltration attempts

    4. **تحلیل TTPS:**
       - Tactics مورد استفاده مهاجمان
       - Techniques رایج
       - Procedures شناسایی شده

    5. **شاخص‌های سازش (IoCs):**
       - IP addresses مشکوک
       - Domain names مخرب
       - File hashes
       - Registry keys
       - Network signatures

    6. **همبستگی با آسیب‌پذیری‌ها:**
       - آسیب‌پذیری‌های بحرانی: {vuln_stats.get('critical', 0)}
       - احتمال بهره‌برداری
       - اولویت‌بندی رفع

    7. **Threat Intelligence:**
       - اطلاعات تهدید جدید
       - پیش‌بینی حملات آینده
       - Threat landscape استان

    8. **پیشنهادات عملیاتی:**
       - قوانین جدید detection
       - بهبود visibility
       - ابزارهای مورد نیاز
       - آموزش تیم

    گزارش باید proactive، عملیاتی و مبتنی بر intelligence باشد.
    از مثال‌های واقعی و use case های عملی استفاده کنید.
    """

    try:
        return await report_generator.generate_report(model, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Training Report ---
@router.post("/training", response_model=Report)
async def generate_training_report(
    model: str = "phi3:mini",
    period_days: int = 30
) -> Report:
    """تولید گزارش آموزش امنیت سایبری"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get training activities
            response = await client.get(f"{BACKEND_BASE_URL}/activities/by-process/TRAINING")
            response.raise_for_status()
            training_activities = response.json()

            # Get organization data
            org_response = await client.get(f"{BACKEND_BASE_URL}/organizations")
            org_response.raise_for_status()
            organizations = org_response.json()

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to backend service: {e}")

    prompt = f"""
    شما مسئول آموزش امنیت سایبری استان هستید. گزارش جامع آموزش‌های انجام شده را تهیه کنید.

    **دوره گزارش:** {period_days} روز گذشته
    **تعداد دوره‌های برگزار شده:** {len(training_activities)}
    **سازمان‌های تحت پوشش:** {len(organizations)}

    **ساختار گزارش آموزش:**

    1. **خلاصه آموزش‌ها:**
       - تعداد دوره‌های برگزار شده
       - تعداد شرکت‌کنندگان
       - سازمان‌های مشارکت‌کننده
       - ساعات آموزشی

    2. **دوره‌های تخصصی:**
       - آموزش SOC Analysts
       - آموزش Incident Response
       - آموزش Secure Coding
       - آموزش Security Awareness
       - آموزش مدیران

    3. **ارزیابی اثربخشی:**
       - نتایج آزمون‌ها
       - میزان رضایت
       - بهبود دانش و مهارت
       - تغییر رفتار امنیتی

    4. **Cyber Range و شبیه‌سازی:**
       - سناریوهای اجرا شده
       - عملکرد تیم‌ها
       - نقاط قوت و ضعف

    5. **آموزش‌های آگاهی‌بخشی:**
       - کمپین‌های اجرا شده
       - Phishing simulation
       - میزان مشارکت کارکنان

    6. **گواهینامه‌ها و مدارک:**
       - تعداد گواهینامه‌های صادر شده
       - Certification paths
       - اعتبارسنجی مدارک

    7. **نیازسنجی آموزشی:**
       - شکاف‌های مهارتی شناسایی شده
       - نیازهای آموزشی آینده
       - اولویت‌بندی دوره‌ها

    8. **برنامه آموزشی آینده:**
       - دوره‌های پیش‌بینی شده
       - تقویم آموزشی
       - بودجه مورد نیاز

    گزارش باید شامل metrics قابل اندازه‌گیری و ROI آموزش باشد.
    """

    try:
        return await report_generator.generate_report(model, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Generic Process Report ---
@router.post("/{process_type}", response_model=Report)
async def generate_process_report(
    process_type: ProcessType = Path(..., description="نوع فرآیند"),
    model: str = "phi3:mini"
) -> Report:
    """تولید گزارش برای فرآیندهای مختلف امنیت سایبری"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get process-specific activities
            response = await client.get(f"{BACKEND_BASE_URL}/activities/by-process/{process_type}")
            response.raise_for_status()
            activities = response.json()

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to backend service: {e}")

    persian_name = get_process_persian_name(process_type)

    prompt = f"""
    شما کارشناس ارشد فرآیند "{persian_name}" هستید. گزارش جامع این فرآیند را تهیه کنید.

    **نوع فرآیند:** {persian_name}
    **تعداد فعالیت‌ها:** {len(activities)}

    **ساختار گزارش:**

    1. **خلاصه اجرایی:**
       - وضعیت کلی فرآیند
       - دستاوردهای کلیدی
       - چالش‌های اصلی

    2. **آمار عملکردی:**
       - تعداد فعالیت‌های انجام شده
       - فعالیت‌های تکمیل شده
       - فعالیت‌های در حال انجام
       - میانگین زمان تکمیل

    3. **تحلیل فعالیت‌ها:**
       - توزیع فعالیت‌ها بر اساس سازمان
       - اولویت‌بندی فعالیت‌ها
       - روند انجام فعالیت‌ها

    4. **نتایج و دستاوردها:**
       - اهداف محقق شده
       - بهبودهای ایجاد شده
       - ارزش افزوده

    5. **مشکلات و موانع:**
       - چالش‌های فنی
       - محدودیت‌های منابع
       - موانع سازمانی

    6. **پیشنهادات بهبود:**
       - بهینه‌سازی فرآیند
       - نیازمندی‌های ابزاری
       - آموزش و توانمندسازی

    7. **برنامه آینده:**
       - اولویت‌های کوتاه‌مدت
       - اهداف بلندمدت
       - منابع مورد نیاز

    گزارش باید متناسب با ماهیت فرآیند "{persian_name}" تنظیم شود.
    از داده‌های واقعی و قابل پیگیری استفاده کنید.
    """

    try:
        return await report_generator.generate_report(model, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))