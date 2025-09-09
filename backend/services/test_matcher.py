import pytest
from models import BusinessInput
from services.matcher import match_requirements

def test_features_any():
    """Test features_any condition - business should match if it has any of the required features"""
    business = BusinessInput(
        size="small",
        seats=20,
        area_sqm=50,
        staff_count=3,
        features=["alcohol", "delivery"]
    )
    
    rules = [
        {
            "id": "alcohol_rule",
            "title": "אלכוהול",
            "category": "רישוי",
            "priority": "High",
            "description": "דרישות לאלכוהול",
            "conditions": {"features_any": ["alcohol"]}
        }
    ]
    
    matches = match_requirements(business, rules)
    assert len(matches) == 1
    assert matches[0].id == "alcohol_rule"
    assert "alcohol" in matches[0].reasons[0]

def test_features_all():
    """Test features_all condition - business must have ALL required features"""
    business = BusinessInput(
        size="small",
        seats=20,
        area_sqm=50,
        staff_count=3,
        features=["alcohol", "delivery"]
    )
    
    rules = [
        {
            "id": "both_features",
            "title": "אלכוהול ומשלוחים",
            "category": "רישוי",
            "priority": "High",
            "description": "דרישות לאלכוהול ומשלוחים",
            "conditions": {"features_all": ["alcohol", "delivery"]}
        },
        {
            "id": "missing_feature",
            "title": "אלכוהול ומוזיקה",
            "category": "רישוי",
            "priority": "High",
            "description": "דרישות לאלכוהול ומוזיקה",
            "conditions": {"features_all": ["alcohol", "music"]}
        }
    ]
    
    matches = match_requirements(business, rules)
    assert len(matches) == 1
    assert matches[0].id == "both_features"
    assert "כל המאפיינים הדרושים קיימים" in matches[0].reasons[0]

def test_features_none():
    """Test features_none condition - business should NOT have any of the forbidden features"""
    business = BusinessInput(
        size="small",
        seats=20,
        area_sqm=50,
        staff_count=3,
        features=["alcohol", "delivery"]
    )
    
    rules = [
        {
            "id": "no_smoking",
            "title": "ללא עישון",
            "category": "בריאות",
            "priority": "Medium",
            "description": "אין עישון",
            "conditions": {"features_none": ["smoking"]}
        },
        {
            "id": "no_alcohol",
            "title": "ללא אלכוהול",
            "category": "בריאות",
            "priority": "Medium",
            "description": "אין אלכוהול",
            "conditions": {"features_none": ["alcohol"]}
        }
    ]
    
    matches = match_requirements(business, rules)
    assert len(matches) == 1
    assert matches[0].id == "no_smoking"
    assert "נבדק שאין מאפיינים אסורים" in matches[0].reasons[0]

def test_numeric_edges_min_seats():
    """Test min_seats boundary values"""
    business = BusinessInput(
        size="medium",
        seats=50,
        area_sqm=100,
        staff_count=5,
        features=[]
    )
    
    rules = [
        {
            "id": "min_50_seats",
            "title": "מינימום 50 מקומות",
            "category": "רישוי",
            "priority": "Medium",
            "description": "מינימום 50 מקומות ישיבה",
            "conditions": {"min_seats": 50}
        },
        {
            "id": "min_51_seats",
            "title": "מינימום 51 מקומות",
            "category": "רישוי",
            "priority": "Medium",
            "description": "מינימום 51 מקומות ישיבה",
            "conditions": {"min_seats": 51}
        }
    ]
    
    matches = match_requirements(business, rules)
    assert len(matches) == 1
    assert matches[0].id == "min_50_seats"
    assert "50≥50" in matches[0].reasons[0]

def test_numeric_edges_max_seats():
    """Test max_seats boundary values"""
    business = BusinessInput(
        size="medium",
        seats=50,
        area_sqm=100,
        staff_count=5,
        features=[]
    )
    
    rules = [
        {
            "id": "max_50_seats",
            "title": "מקסימום 50 מקומות",
            "category": "רישוי",
            "priority": "Medium",
            "description": "מקסימום 50 מקומות ישיבה",
            "conditions": {"max_seats": 50}
        },
        {
            "id": "max_49_seats",
            "title": "מקסימום 49 מקומות",
            "category": "רישוי",
            "priority": "Medium",
            "description": "מקסימום 49 מקומות ישיבה",
            "conditions": {"max_seats": 49}
        }
    ]
    
    matches = match_requirements(business, rules)
    assert len(matches) == 1
    assert matches[0].id == "max_50_seats"
    assert "50≤50" in matches[0].reasons[0]

def test_numeric_edges_area():
    """Test min/max area boundary values"""
    business = BusinessInput(
        size="medium",
        seats=50,
        area_sqm=100,
        staff_count=5,
        features=[]
    )
    
    rules = [
        {
            "id": "min_100_area",
            "title": "מינימום 100 מ״ר",
            "category": "רישוי",
            "priority": "Medium",
            "description": "מינימום 100 מ״ר",
            "conditions": {"min_area_sqm": 100}
        },
        {
            "id": "max_100_area",
            "title": "מקסימום 100 מ״ר",
            "category": "רישוי",
            "priority": "Medium",
            "description": "מקסימום 100 מ״ר",
            "conditions": {"max_area_sqm": 100}
        }
    ]
    
    matches = match_requirements(business, rules)
    assert len(matches) == 2
    assert any("שטח 100≥100" in match.reasons[0] for match in matches)
    assert any("שטח 100≤100" in match.reasons[0] for match in matches)

def test_numeric_edges_staff():
    """Test min/max staff boundary values"""
    business = BusinessInput(
        size="medium",
        seats=50,
        area_sqm=100,
        staff_count=5,
        features=[]
    )
    
    rules = [
        {
            "id": "min_5_staff",
            "title": "מינימום 5 עובדים",
            "category": "רישוי",
            "priority": "Medium",
            "description": "מינימום 5 עובדים",
            "conditions": {"min_staff": 5}
        },
        {
            "id": "max_5_staff",
            "title": "מקסימום 5 עובדים",
            "category": "רישוי",
            "priority": "Medium",
            "description": "מקסימום 5 עובדים",
            "conditions": {"max_staff": 5}
        }
    ]
    
    matches = match_requirements(business, rules)
    assert len(matches) == 2
    assert any("צוות 5≥5" in match.reasons[0] for match in matches)
    assert any("צוות 5≤5" in match.reasons[0] for match in matches)

def test_size_any_filter():
    """Test size_any filter"""
    business = BusinessInput(
        size="small",
        seats=20,
        area_sqm=50,
        staff_count=3,
        features=[]
    )
    
    rules = [
        {
            "id": "small_business",
            "title": "עסק קטן",
            "category": "רישוי",
            "priority": "Medium",
            "description": "עסק קטן",
            "conditions": {"size_any": ["small", "medium"]}
        },
        {
            "id": "large_business",
            "title": "עסק גדול",
            "category": "רישוי",
            "priority": "Medium",
            "description": "עסק גדול",
            "conditions": {"size_any": ["large"]}
        }
    ]
    
    matches = match_requirements(business, rules)
    assert len(matches) == 1
    assert matches[0].id == "small_business"
    assert "סוג העסק 'small' נכלל ב-size_any" in matches[0].reasons[0]

def test_rule_with_no_conditions():
    """Test rule with no conditions should match any business"""
    business = BusinessInput(
        size="small",
        seats=20,
        area_sqm=50,
        staff_count=3,
        features=[]
    )
    
    rules = [
        {
            "id": "general_rule",
            "title": "כלל כללי",
            "category": "כללי",
            "priority": "Low",
            "description": "כלל כללי ללא תנאים",
            "conditions": {}
        }
    ]
    
    matches = match_requirements(business, rules)
    assert len(matches) == 1
    assert matches[0].id == "general_rule"
    assert "כללי — ללא תנאים" in matches[0].reasons[0]

def test_priority_sorting():
    """Test that results are sorted by priority (High > Medium > Low)"""
    business = BusinessInput(
        size="small",
        seats=20,
        area_sqm=50,
        staff_count=3,
        features=["alcohol"]
    )
    
    rules = [
        {
            "id": "low_priority",
            "title": "עדיפות נמוכה",
            "category": "A",
            "priority": "Low",
            "description": "עדיפות נמוכה",
            "conditions": {"features_any": ["alcohol"]}
        },
        {
            "id": "high_priority",
            "title": "עדיפות גבוהה",
            "category": "A",
            "priority": "High",
            "description": "עדיפות גבוהה",
            "conditions": {"features_any": ["alcohol"]}
        },
        {
            "id": "medium_priority",
            "title": "עדיפות בינונית",
            "category": "A",
            "priority": "Medium",
            "description": "עדיפות בינונית",
            "conditions": {"features_any": ["alcohol"]}
        }
    ]
    
    matches = match_requirements(business, rules)
    assert len(matches) == 3
    assert matches[0].priority == "High"
    assert matches[1].priority == "Medium"
    assert matches[2].priority == "Low"

def test_complex_conditions():
    """Test complex combination of conditions"""
    business = BusinessInput(
        size="medium",
        seats=75,
        area_sqm=150,
        staff_count=6,
        features=["alcohol", "delivery", "music"]
    )
    
    rules = [
        {
            "id": "complex_rule",
            "title": "כלל מורכב",
            "category": "רישוי",
            "priority": "High",
            "description": "כלל מורכב עם מספר תנאים",
            "conditions": {
                "size_any": ["medium", "large"],
                "min_seats": 50,
                "max_seats": 100,
                "min_area_sqm": 100,
                "features_any": ["alcohol"],
                "features_all": ["delivery"],
                "features_none": ["smoking"]
            }
        }
    ]
    
    matches = match_requirements(business, rules)
    assert len(matches) == 1
    assert matches[0].id == "complex_rule"
    # Should have multiple reasons
    assert len(matches[0].reasons) > 1
    # Check for specific reason types
    reasons_text = " ".join(matches[0].reasons)
    assert "size_any" in reasons_text
    assert "75≥50" in reasons_text
    assert "75≤100" in reasons_text
    assert "שטח 150≥100" in reasons_text
    assert "alcohol" in reasons_text
    assert "delivery" in reasons_text
    assert "smoking" in reasons_text

if __name__ == "__main__":
    # Run tests manually
    test_features_any()
    test_features_all()
    test_features_none()
    test_numeric_edges_min_seats()
    test_numeric_edges_max_seats()
    test_numeric_edges_area()
    test_numeric_edges_staff()
    test_size_any_filter()
    test_rule_with_no_conditions()
    test_priority_sorting()
    test_complex_conditions()
    print("All tests passed!")
