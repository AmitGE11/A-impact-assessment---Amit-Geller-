import os
import logging
from typing import Dict, Any

log = logging.getLogger("report")


def _mock_report(business: Dict[str, Any], matches: Dict[str, Any]) -> str:
    name = business.get("name") or "העסק"
    seats = business.get("seats")
    total = matches.get("matches_total")
    return (
        f"זהו דוח הדגמה (Mock) עבור {name}.\n"
        f"מספר מקומות ישיבה: {seats}\n"
        f"סה״כ התאמות רגולטוריות שנמצאו: {total}\n"
        f"— זה רק דמו. הפעל ספק AI אמיתי כדי לקבל דוח מלא."
    )


def _gemini_report(business: Dict[str, Any], matches: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a concise Hebrew report using Google Gemini."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing")

    try:
        import google.generativeai as genai
    except Exception:
        log.exception("Gemini SDK import failed")
        raise

    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    system_prompt = (
        "אתה עוזר רגולטורי. קבל פרופיל עסק והתאמות לרגולציה, "
        "הפק דו\"ח תמציתי בעברית הכולל: סיכום עסקי קצר, סיכום תקנות עיקריות, "
        "רשימת פעולות לביצוע (נקודות), והערות/סיכונים מיוחדים אם קיימים."
    )

    user_payload = {
        "business": business,
        "summary": {
            "matches_total": matches.get("matches_total"),
            "high_risk": len([m for m in matches.get("items", []) if m.get("severity") == "high"]),
            "medium_risk": len([m for m in matches.get("items", []) if m.get("severity") == "medium"]),
        },
        # cap requirements to keep prompt short
        "requirements": matches.get("items", [])[:50],
    }

    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"{system_prompt}\n\n## נתוני קלט (JSON)\n{user_payload}"
        resp = model.generate_content(prompt)

        text = getattr(resp, "text", None)
        if not text and getattr(resp, "candidates", None):
            parts = getattr(resp.candidates[0].content, "parts", []) or []
            if parts and hasattr(parts[0], "text"):
                text = parts[0].text

        if not text:
            text = "לא התקבלה תשובה מהמודל."

        return {
            "report": text,
            "metadata": {"mode": "ai", "provider": "gemini", "model": model_name},
        }
    except Exception:
        log.exception("Gemini generation failed")
        raise


def _openai_report(business: Dict[str, Any], matches: Dict[str, Any]) -> Dict[str, Any]:
    """Optional: if OPENAI support exists in the project, keep a placeholder."""
    return {
        "report": "OpenAI integration is not configured in this build.",
        "metadata": {"mode": "ai", "provider": "openai"},
    }


def generate_report(business: dict, matches: dict) -> dict:
    provider = (os.getenv("PROVIDER") or "mock").strip().lower()
    log.info("AI provider configured: %s", provider)

    if provider == "gemini":
        return _gemini_report(business, matches)
    elif provider == "openai":
        return _openai_report(business, matches)
    else:
        return {
            "report": _mock_report(business, matches),
            "metadata": {"mode": "mock", "provider": "mock"},
        }