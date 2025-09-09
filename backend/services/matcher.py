from typing import List, Dict, Any
from models import BusinessInput, RequirementItem

def match_requirements(business: BusinessInput, rules: List[Dict[str, Any]]) -> List[RequirementItem]:
    """
    Match business profile against requirements based on conditions.
    
    Args:
        business: Business profile with size, seats, and features
        rules: List of requirement dictionaries from JSON data
        
    Returns:
        List of matching RequirementItem objects, sorted by priority, category, then id
        
    Note:
        Available business features for matching rules:
        - Basic: gas, meat, delivery
        - Service: alcohol, outdoor, music, smoking, night, takeaway
        - Kitchen: kitchen_hot, kitchen_cold, dairy, fish, vegan
        
        Use features_any, features_all, or features_none in conditions to match these features.
    """
    matched = []
    
    for rule in rules:
        if _matches_conditions(business, rule.get("conditions", {})):
            # Convert dict to RequirementItem
            requirement = RequirementItem(
                id=rule["id"],
                title=rule["title"],
                category=rule["category"],
                priority=rule["priority"],
                description=rule["description"],
                conditions=rule.get("conditions", {})
            )
            matched.append(requirement)
    
    # Sort by priority (High > Medium > Low), then category, then id
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    matched.sort(key=lambda x: (priority_order[x.priority], x.category, x.id))
    
    return matched

def _matches_conditions(business: BusinessInput, conditions: Dict[str, Any]) -> bool:
    """
    Check if business matches all provided conditions.
    All conditions must be satisfied (AND logic).
    """
    # size_any: business.size must be in the list
    if "size_any" in conditions:
        if business.size not in conditions["size_any"]:
            return False
    
    # min_seats: business.seats must be >= min_seats
    if "min_seats" in conditions:
        if business.seats < conditions["min_seats"]:
            return False
    
    # max_seats: business.seats must be <= max_seats
    if "max_seats" in conditions:
        if business.seats > conditions["max_seats"]:
            return False
    
    # features_any: intersection between business.features and conditions must not be empty
    if "features_any" in conditions:
        if not set(business.features) & set(conditions["features_any"]):
            return False
    
    # features_all: all features in conditions must be present in business.features
    if "features_all" in conditions:
        if not set(conditions["features_all"]).issubset(set(business.features)):
            return False
    
    # features_none: none of the features in conditions should be present in business.features
    if "features_none" in conditions:
        if set(business.features) & set(conditions["features_none"]):
            return False
    
    return True

if __name__ == "__main__":
    # Simple test cases
    from models import BusinessInput
    
    # Test business profiles
    small_restaurant = BusinessInput(size="small", seats=20, features=["meat", "gas"])
    large_cafe = BusinessInput(size="large", seats=100, features=["delivery"])
    medium_bakery = BusinessInput(size="medium", seats=50, features=["gas"])
    
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
        }
    ]
    
    # Test matching
    print("Testing small restaurant (meat + gas):")
    matches = match_requirements(small_restaurant, test_rules)
    for match in matches:
        print(f"  - {match.title} ({match.priority})")
    
    print("\nTesting large cafe (delivery, 100 seats):")
    matches = match_requirements(large_cafe, test_rules)
    for match in matches:
        print(f"  - {match.title} ({match.priority})")
    
    print("\nTesting medium bakery (gas only, 50 seats):")
    matches = match_requirements(medium_bakery, test_rules)
    for match in matches:
        print(f"  - {match.title} ({match.priority})")
