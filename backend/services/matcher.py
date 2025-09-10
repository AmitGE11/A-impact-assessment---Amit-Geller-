from typing import List, Dict, Any, Generator
from models import BusinessInput, MatchItem

# Feature mapping from English keys to Hebrew names
FEATURE_NAMES = {
    "gas": "גז",
    "meat": "בשר", 
    "delivery": "משלוחים",
    "alcohol": "הגשת אלכוהול",
    "outdoor": "מקומות ישיבה חיצוניים",
    "music": "מוסיקה/בידור",
    "smoking": "אזור עישון",
    "kitchen_hot": "מטבח חם",
    "kitchen_cold": "מטבח קר בלבד",
    "dairy": "מזון חלבי",
    "fish": "מזון דגים",
    "vegan": "טבעוני",
    "night": "פתוח אחרי חצות",
    "takeaway": "איסוף עצמי",
    "grease_trap": "מלכודת שומן",
    "hood_vent": "מנדף/מערכת יניקה תקינה",
    "fire_ext": "מטפי כיבוי ניידים",
    "sprinkler": "מערכת מתזים/ספרינקלרים",
    "handwash": "עמדות שטיפת ידיים",
    "refrigeration": "קירור מסחרי",
    "freezer": "מקפיא/הקפאה",
    "allergen_note": "הצהרת אלרגנים בתפריט",
    "accessibility": "נגישות לנכים",
    "signage": "רישיון ושילוט במקום בולט",
    "pest_control": "הדברה תקופתית",
    "waste_sep": "הפרדת פסולת/שמן בישול",
    "gas_cert": "בדיקת גז בתוקף"
}

def get_feature_names(features: List[str]) -> List[str]:
    """Convert English feature keys to Hebrew names."""
    return [FEATURE_NAMES.get(feature, feature) for feature in features]

def match_requirements(business: BusinessInput, rules: List[Dict[str, Any]]) -> List[MatchItem]:
    """
    Match business profile against requirements based on conditions with explanations.
    
    Args:
        business: Business profile with size, seats, area, staff, and features
        rules: List of requirement dictionaries from JSON data
        
    Returns:
        List of matching MatchItem objects with explanations, sorted by priority, category, then title
    """
    matched = list(_match_requirements_generator(business, rules))
    
    # Sort by priority weight {"High":0, "Medium":1, "Low":2}, then category, then title
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    matched.sort(key=lambda x: (priority_order[x.priority], x.category, x.title))
    
    return matched

def _match_requirements_generator(business: BusinessInput, rules: List[Dict[str, Any]]) -> Generator[MatchItem, None, None]:
    """
    Generator that yields matching rules with explanations.
    """
    for r in rules:
        cond = r.get("conditions", {})  # may be missing keys
        checks = []
        reasons = []

        # size_any
        if cond.get("size_any"):
            ok = business.size in cond["size_any"]
            checks.append(ok)
            if ok: 
                reasons.append(f"סוג העסק '{business.size}' נכלל ב-size_any")

        # seats
        for k, sign, val in [("min_seats", ">=", cond.get("min_seats")),
                             ("max_seats", "<=", cond.get("max_seats"))]:
            if val is not None:
                ok = (business.seats >= val) if "min" in k else (business.seats <= val)
                checks.append(ok)
                if ok: 
                    reasons.append(f"{business.seats}{'≥' if 'min' in k else '≤'}{val} ⇒ {k}")

        # area
        for k, val in [("min_area_sqm", cond.get("min_area_sqm")),
                       ("max_area_sqm", cond.get("max_area_sqm"))]:
            if val is not None:
                ok = (business.area_sqm >= val) if "min" in k else (business.area_sqm <= val)
                checks.append(ok)
                if ok: 
                    reasons.append(f"שטח {business.area_sqm}{'≥' if 'min' in k else '≤'}{val} ⇒ {k}")

        # staff
        for k, val in [("min_staff", cond.get("min_staff")),
                       ("max_staff", cond.get("max_staff"))]:
            if val is not None:
                ok = (business.staff_count >= val) if "min" in k else (business.staff_count <= val)
                checks.append(ok)
                if ok: 
                    reasons.append(f"צוות {business.staff_count}{'≥' if 'min' in k else '≤'}{val} ⇒ {k}")

        # features_any / all / none
        fa = set(cond.get("features_any", []))
        fall = set(cond.get("features_all", []))
        fnone = set(cond.get("features_none", []))
        bset = set(business.features or [])
        
        if fa:
            ok = bool(bset & fa)
            checks.append(ok)
            if ok: 
                matched_features = sorted(list(bset & fa))
                hebrew_names = get_feature_names(matched_features)
                for feature, hebrew_name in zip(matched_features, hebrew_names):
                    reasons.append(f"מאפיין זוהה : {hebrew_name}")
        
        if fall:
            ok = fall.issubset(bset)
            checks.append(ok)
            if ok: 
                required_features = sorted(list(fall))
                hebrew_names = get_feature_names(required_features)
                for feature, hebrew_name in zip(required_features, hebrew_names):
                    reasons.append(f"מאפיין נדרש : {hebrew_name}")
        
        if fnone:
            ok = not (bset & fnone)
            checks.append(ok)
            if ok: 
                forbidden_features = sorted(list(fnone))
                hebrew_names = get_feature_names(forbidden_features)
                for feature, hebrew_name in zip(forbidden_features, hebrew_names):
                    reasons.append(f"מאפיין אסור לא קיים : {hebrew_name}")

        # if no conditions at all → treat as general rule (match everything)
        if not any([cond.get("size_any"), cond.get("min_seats") is not None, cond.get("max_seats") is not None,
                    cond.get("min_area_sqm") is not None, cond.get("max_area_sqm") is not None,
                    cond.get("min_staff") is not None, cond.get("max_staff") is not None,
                    fa, fall, fnone]):
            checks.append(True)
            reasons.append("כללי — ללא תנאים")

        if all(checks):
            yield MatchItem(
                id=r.get("id", ""),
                category=r.get("category", ""),
                title=r.get("title", "").strip() or "(ללא כותרת)",
                description=r.get("description", "").strip(),
                priority=r.get("priority", "Medium"),
                reasons=reasons
            )

if __name__ == "__main__":
    # Simple test cases
    from models import BusinessInput
    
    # Test business profiles
    small_restaurant = BusinessInput(
        size="small", 
        seats=20, 
        area_sqm=50, 
        staff_count=3, 
        features=["meat", "gas"]
    )
    large_cafe = BusinessInput(
        size="large", 
        seats=100, 
        area_sqm=200, 
        staff_count=8, 
        features=["delivery"]
    )
    medium_bakery = BusinessInput(
        size="medium", 
        seats=50, 
        area_sqm=100, 
        staff_count=5, 
        features=["gas"]
    )
    
    # Test requirements
    test_rules = [
        {
            "id": "gas_safety",
            "title": "בטיחות גז",
            "category": "בטיחות",
            "priority": "High",
            "description": "דרישות בטיחות למערכות גז",
            "conditions": {"features_any": ["gas"]}
        },
        {
            "id": "meat_handling",
            "title": "טיפול בבשר",
            "category": "היגיינה",
            "priority": "High",
            "description": "דרישות היגיינה לטיפול בבשר",
            "conditions": {"features_any": ["meat"]}
        },
        {
            "id": "large_seating",
            "title": "ישיבה למקומות רבים",
            "category": "רישוי כללי",
            "priority": "Medium",
            "description": "דרישות מיוחדות למקומות עם מעל 80 מקומות ישיבה",
            "conditions": {"min_seats": 80}
        },
        {
            "id": "general_rule",
            "title": "כללי",
            "category": "כללי",
            "priority": "Low",
            "description": "כלל כללי ללא תנאים",
            "conditions": {}
        }
    ]
    
    # Test matching
    print("Testing small restaurant (meat + gas):")
    matches = match_requirements(small_restaurant, test_rules)
    for match in matches:
        print(f"  - {match.title} ({match.priority})")
        for reason in match.reasons:
            print(f"    * {reason}")
    
    print("\nTesting large cafe (delivery, 100 seats):")
    matches = match_requirements(large_cafe, test_rules)
    for match in matches:
        print(f"  - {match.title} ({match.priority})")
        for reason in match.reasons:
            print(f"    * {reason}")
    
    print("\nTesting medium bakery (gas only, 50 seats):")
    matches = match_requirements(medium_bakery, test_rules)
    for match in matches:
        print(f"  - {match.title} ({match.priority})")
        for reason in match.reasons:
            print(f"    * {reason}")