from pathlib import Path
from dotenv import load_dotenv, dotenv_values

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH, override=True, encoding="utf-8")

import os
if not (os.getenv("PROVIDER") or "").strip():
    vals = dotenv_values(ENV_PATH)
    os.environ.update({k:str(v) for k,v in vals.items() if v is not None})

import logging
import requests
from typing import List
from models import BusinessInput, RequirementItem, ReportRequest

# Logger
log = logging.getLogger("report")

def _get_provider() -> str:
    return (os.getenv("PROVIDER") or "mock").strip().lower()

def _get_gemini_key() -> str | None:
    return os.getenv("GEMINI_API_KEY")

def _get_openai_key() -> str | None:
    return os.getenv("OPENAI_API_KEY")

def _get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def _gemini_extract_text(data: dict) -> str:
    """Safely extract text from Gemini API response."""
    try:
        cands = data.get("candidates", [])
        if not cands: 
            return ""
        parts = cands[0].get("content", {}).get("parts", [])
        if not parts: 
            return ""
        return parts[0].get("text", "").strip()
    except Exception:
        return ""

def build_prompt(business: BusinessInput, matched: List[RequirementItem]) -> str:
    """
    Build a Hebrew prompt for the LLM to generate a compliance report.
    """
    # Group requirements by category and priority
    categories = {}
    for req in matched:
        if req.category not in categories:
            categories[req.category] = {"High": [], "Medium": [], "Low": []}
        categories[req.category][req.priority].append(req)
    
    prompt = f"""אתה מומחה לרישוי עסקים בישראל. אנא צור דוח מפורט בעברית לעסק עם הפרופיל הבא:

**פרופיל העסק:**
- שם העסק: {business.business_name}
- גודל: {business.size}
- מספר מקומות ישיבה: {business.seats}
- שטח העסק: {business.area_sqm} מ"ר
- מספר עובדים במשמרת: {business.staff_count}
- מאפיינים: {', '.join(business.features) if business.features else 'ללא מאפיינים מיוחדים'}

**דרישות רישוי רלוונטיות:**
"""
    
    for category, priorities in categories.items():
        prompt += f"\n**{category}:**\n"
        for priority in ["High", "Medium", "Low"]:
            if priorities[priority]:
                prompt += f"\n{priority} עדיפות:\n"
                for req in priorities[priority]:
                    prompt += f"- {req.title}: {req.description}\n"
    
    prompt += """

**אנא צור דוח הכולל:**

1. **סיכום תקנות רלוונטיות** - הסבר פשוט וברור של התקנות החשובות
2. **ארגון לפי קטגוריות** - חלוקה ברורה לפי תחומי האחריות
3. **רשימת פעולות לפי עדיפות** - מה צריך לעשות קודם (High עדיפות ראשונה)
4. **3 צעדים קונקרטיים הבאים** - מה העסק צריך לעשות עכשיו

הדוח צריך להיות מקצועי, ברור ומועיל לעסק להבין מה נדרש ממנו.
"""
    
    return prompt

def _gemini_report(business: BusinessInput, matches: List[RequirementItem]) -> dict:
    """Generate a compliance report using Google Gemini API."""
    api_key = _get_gemini_key()
    if not api_key:
        log.warning("Gemini selected but no API key found; falling back to mock.")
        return {
            "report": _generate_mock_report(business, matches),
            "metadata": {"mode": "mock", "provider": "gemini", "reason": "missing_key"}
        }
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    prompt = build_prompt(business, matches)
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        log.info("Calling Gemini generateContent (len(prompt)=%s)", len(prompt))
        r = requests.post(url, json=body, timeout=60)
        log.info("Gemini HTTP %s", r.status_code)
        
        if r.status_code != 200:
            return {
                "report": _generate_mock_report(business, matches) + f"\n\n> Gemini error {r.status_code}",
                "metadata": {"mode": "mock", "provider": "gemini", "http": r.status_code}
            }
        
        data = r.json()
        text = _gemini_extract_text(data)
        if not text:
            log.warning("Gemini returned 200 but empty text.")
            return {
                "report": _generate_mock_report(business, matches) + "\n\n> Gemini returned empty content.",
                "metadata": {"mode": "mock", "provider": "gemini", "http": 200}
            }
        
        return {
            "report": text, 
            "metadata": {"mode": "live", "provider": "gemini"}
        }
    except Exception as e:
        log.exception("Gemini exception")
        return {
            "report": _generate_mock_report(business, matches) + f"\n\n> Gemini exception: {e}",
            "metadata": {"mode": "mock", "provider": "gemini", "exception": True}
        }

def _openai_report(business: BusinessInput, matches: List[RequirementItem]) -> dict:
    """Generate a compliance report using OpenAI API."""
    from openai import OpenAI, RateLimitError, APIError, APITimeoutError
    
    key = _get_openai_key()
    if not key:
        log.warning("OpenAI selected but no API key found; falling back to mock.")
        return {
            "report": _generate_mock_report(business, matches),
            "metadata": {"mode": "mock", "provider": "openai", "reason": "missing_key"}
        }
    
    client = OpenAI(api_key=key)
    model = _get_openai_model()
    prompt = build_prompt(business, matches)
    
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "אתה יועץ רגולציה. כתוב בעברית פשוטה ועניינית."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
            timeout=30,
        )
        text = resp.choices[0].message.content.strip()
        return {
            "report": text, 
            "metadata": {"mode": "live", "provider": "openai", "model": model}
        }
    except Exception as e:
        log.exception("OpenAI exception")
        return {
            "report": _generate_mock_report(business, matches) + f"\n\n> OpenAI exception: {e}",
            "metadata": {"mode": "mock", "provider": "openai", "exception": True}
        }

def generate_report(business, matches):
    """Generate a compliance report using the configured provider (OpenAI, Gemini, or Mock)."""
    provider = _get_provider()
    log.info("AI provider configured: %s", provider)
    
    if provider == "gemini":
        return _gemini_report(business, matches)
    if provider == "openai":
        return _openai_report(business, matches)
    return {
        "report": _generate_mock_report(business, matches),
        "metadata": {"mode": "mock", "provider": "mock"}
    }

def _generate_mock_report(business: BusinessInput, requirements: List[RequirementItem]) -> str:
    """
    Generate a well-structured Hebrew mock report when OpenAI API is not available.
    """
    # Group requirements by category and priority
    categories = {}
    for req in requirements:
        if req.category not in categories:
            categories[req.category] = {"High": [], "Medium": [], "Low": []}
        categories[req.category][req.priority].append(req)
    
    report = f"""# דוח רישוי עסק - {business.business_name}

## סיכום עסקי
**פרופיל העסק:**
- שם העסק: {business.business_name}
- גודל: {business.size}
- מספר מקומות ישיבה: {business.seats}
- שטח העסק: {business.area_sqm} מ"ר
- מספר עובדים במשמרת: {business.staff_count}
- מאפיינים: {', '.join(business.features) if business.features else 'ללא מאפיינים מיוחדים'}

---

## 1. סיכום תקנות רלוונטיות

העסק שלך נדרש לעמוד בתקנות רישוי עסקים של מדינת ישראל. התקנות מחולקות לקטגוריות שונות ונועדו להבטיח בטיחות, היגיינה ותפעול תקין.

"""

    # Add category summaries
    for category, priorities in categories.items():
        report += f"### {category}\n"
        high_count = len(priorities["High"])
        medium_count = len(priorities["Medium"])
        low_count = len(priorities["Low"])
        
        if high_count > 0:
            report += f"**{high_count} דרישות בעדיפות גבוהה** - דורש טיפול מיידי\n"
        if medium_count > 0:
            report += f"**{medium_count} דרישות בעדיפות בינונית** - דורש טיפול תוך חודש\n"
        if low_count > 0:
            report += f"**{low_count} דרישות בעדיפות נמוכה** - דורש טיפול תוך 3 חודשים\n"
        report += "\n"

    report += """---

## 2. ארגון לפי קטגוריות

"""

    # Detailed requirements by category
    for category, priorities in categories.items():
        report += f"### {category}\n\n"
        
        for priority in ["High", "Medium", "Low"]:
            if priorities[priority]:
                priority_hebrew = {"High": "גבוהה", "Medium": "בינונית", "Low": "נמוכה"}
                report += f"**עדיפות {priority_hebrew[priority]}:**\n"
                for req in priorities[priority]:
                    report += f"- **{req.title}**: {req.description}\n"
                report += "\n"

    report += """---

## 3. רשימת פעולות לפי עדיפות

### עדיפות גבוהה (High) - טיפול מיידי
"""

    high_requirements = []
    for category, priorities in categories.items():
        high_requirements.extend(priorities["High"])
    
    if high_requirements:
        for i, req in enumerate(high_requirements, 1):
            report += f"{i}. **{req.title}** ({req.category})\n"
            report += f"   {req.description}\n\n"
    else:
        report += "אין דרישות בעדיפות גבוהה.\n\n"

    report += """### עדיפות בינונית (Medium) - טיפול תוך חודש
"""

    medium_requirements = []
    for category, priorities in categories.items():
        medium_requirements.extend(priorities["Medium"])
    
    if medium_requirements:
        for i, req in enumerate(medium_requirements, 1):
            report += f"{i}. **{req.title}** ({req.category})\n"
            report += f"   {req.description}\n\n"
    else:
        report += "אין דרישות בעדיפות בינונית.\n\n"

    report += """### עדיפות נמוכה (Low) - טיפול תוך 3 חודשים
"""

    low_requirements = []
    for category, priorities in categories.items():
        low_requirements.extend(priorities["Low"])
    
    if low_requirements:
        for i, req in enumerate(low_requirements, 1):
            report += f"{i}. **{req.title}** ({req.category})\n"
            report += f"   {req.description}\n\n"
    else:
        report += "אין דרישות בעדיפות נמוכה.\n\n"

    report += """---

## 4. 3 צעדים קונקרטיים הבאים

### צעד 1: בדיקה ראשונית
- בדוק את כל הדרישות בעדיפות גבוהה
- ודא שיש לך את כל המסמכים הנדרשים
- צור רשימת פעולות עם תאריכי יעד

### צעד 2: פנייה לרשויות
- פנה לרשות הרישוי המקומית
- קבל מידע על הליכי הרישוי הספציפיים
- בדוק אם יש צורך ברישיונות נוספים

### צעד 3: הכנת מסמכים
- אסוף את כל המסמכים הנדרשים
- הכנת תוכניות וציורים אם נדרש
- הגש בקשה לרישוי עסק

---

**הערה:** דוח זה מבוסס על מידע כללי. מומלץ להתייעץ עם מומחה רישוי עסקים לקבלת ייעוץ ספציפי לעסק שלך.

*נוצר על ידי Licensure Buddy IL - מערכת סיוע לרישוי עסקים בישראל*
"""

    return report
