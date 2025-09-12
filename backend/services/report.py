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


def _gemini_report(business, requirements):
    """
    Accept a list of requirement items and build a stable payload for Gemini.
    """
    items = requirements or []
    # Normalize business whether it's a model or dict
    def _get(obj, name):
        return getattr(obj, name, None) if hasattr(obj, name) else (obj.get(name) if isinstance(obj, dict) else None)
    payload = {
        "business": {
            "business_name": _get(business, "business_name"),
            "size": _get(business, "size"),
            "seats": _get(business, "seats"),
            "area_sqm": _get(business, "area_sqm"),
            "staff_count": _get(business, "staff_count"),
            "features": _get(business, "features"),
        },
        "matches_total": len(items),
        "items": [
            {
                "id": str(_get(it, "id")),
                "title": _get(it, "title"),
                "category": _get(it, "category"),
                "priority": _get(it, "priority"),
                "description": _get(it, "description"),
                "conditions": _get(it, "conditions") or {},
            }
            for it in items
        ],
    }

    # Build the prompt and call Gemini here (existing logic), but use `payload`
    # instead of assuming dict shape for matches.
    return _call_gemini_with_payload(payload)


def _call_gemini_with_payload(payload):
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
        "business": payload["business"],
        "summary": {
            "matches_total": payload["matches_total"],
            "high_risk": len([m for m in payload["items"] if m.get("priority") == "High"]),
            "medium_risk": len([m for m in payload["items"] if m.get("priority") == "Medium"]),
        },
        # cap requirements to keep prompt short
        "requirements": payload["items"][:50],
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


def generate_report(business, requirements):
    """
    `requirements` is a List[RequirementItem]-like sequence (id, title, category, priority, description, conditions?).
    """
    provider = (os.getenv("PROVIDER") or "mock").strip().lower()
    log.info("AI provider configured: %s", provider)

    if provider == "gemini":
        return _gemini_report(business, requirements)
    elif provider == "openai":
        return _openai_report(business, requirements)
    else:
        # For mock mode, convert requirements to the old format
        items = requirements or []
        matches_dict = {
            "matches_total": len(items),
            "items": [
                {
                    "id": str(getattr(it, "id", None) or it.get("id")),
                    "title": getattr(it, "title", None) or it.get("title"),
                    "category": getattr(it, "category", None) or it.get("category"),
                    "priority": getattr(it, "priority", None) or it.get("priority"),
                    "description": getattr(it, "description", None) or it.get("description"),
                    "conditions": getattr(it, "conditions", None) or it.get("conditions", {}),
                }
                for it in items
            ]
        }
        return {
            "report": _mock_report(business, matches_dict),
            "metadata": {"mode": "mock", "provider": "mock"},
        }