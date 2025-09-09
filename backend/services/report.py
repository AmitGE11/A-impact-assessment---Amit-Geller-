import os
from typing import List
from models import BusinessInput, RequirementItem, ReportRequest

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
- גודל: {business.size}
- מספר מקומות ישיבה: {business.seats}
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

def generate_report(request: ReportRequest) -> str:
    """
    Generate a compliance report using OpenAI API or return a mock report.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    if not api_key or api_key == "sk-xxx":
        return _generate_mock_report(request.business, request.requirements)
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        prompt = build_prompt(request.business, request.requirements)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "אתה מומחה לרישוי עסקים בישראל. תמיד ענה בעברית."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Fallback to mock report if API fails
        return _generate_mock_report(request.business, request.requirements)

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
    
    report = f"""# דוח רישוי עסק - Licensure Buddy IL

## סיכום עסקי
**פרופיל העסק:**
- גודל: {business.size}
- מספר מקומות ישיבה: {business.seats}
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
