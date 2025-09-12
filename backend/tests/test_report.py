import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from models import ReportRequest, BusinessInput, RequirementItem
from main import app

client = TestClient(app)

def test_report_request_model_with_matches_field():
    """Test ReportRequest model accepts 'matches' field directly"""
    business = BusinessInput(
        business_name="Test Business",
        size="small",
        seats=10,
        area_sqm=50,
        staff_count=2,
        features=["gas"]
    )
    
    requirements = [
        RequirementItem(
            id="req1",
            title="Test Requirement",
            category="Test",
            priority="High",
            description="Test description"
        )
    ]
    
    # Test with 'matches' field (new API)
    request_data = {
        "business": business.model_dump(),
        "matches": [req.model_dump() for req in requirements]
    }
    
    report_request = ReportRequest(**request_data)
    assert report_request.business.business_name == "Test Business"
    assert len(report_request.matches) == 1
    assert report_request.matches[0].id == "req1"

def test_report_request_model_with_requirements_alias():
    """Test ReportRequest model accepts 'requirements' field via alias (backward compatibility)"""
    business = BusinessInput(
        business_name="Test Business",
        size="small",
        seats=10,
        area_sqm=50,
        staff_count=2,
        features=["gas"]
    )
    
    requirements = [
        RequirementItem(
            id="req1",
            title="Test Requirement",
            category="Test",
            priority="High",
            description="Test description"
        )
    ]
    
    # Test with 'requirements' field (old API - should work via alias)
    request_data = {
        "business": business.model_dump(),
        "requirements": [req.model_dump() for req in requirements]
    }
    
    report_request = ReportRequest(**request_data)
    assert report_request.business.business_name == "Test Business"
    assert len(report_request.matches) == 1
    assert report_request.matches[0].id == "req1"

def test_report_request_model_validation_error():
    """Test ReportRequest model validation with missing required fields"""
    business = BusinessInput(
        business_name="Test Business",
        size="small",
        seats=10,
        area_sqm=50,
        staff_count=2,
        features=["gas"]
    )
    
    # Test with missing 'matches'/'requirements' field
    request_data = {
        "business": business.model_dump()
    }
    
    with pytest.raises(ValidationError) as exc_info:
        ReportRequest(**request_data)
    
    assert "requirements" in str(exc_info.value)

def test_api_report_endpoint_with_matches():
    """Test /api/report endpoint with 'matches' field"""
    business = {
        "business_name": "Test Business",
        "size": "small",
        "seats": 10,
        "area_sqm": 50,
        "staff_count": 2,
        "features": ["gas"]
    }
    
    requirements = [
        {
            "id": "req1",
            "title": "Test Requirement",
            "category": "Test",
            "priority": "High",
            "description": "Test description"
        }
    ]
    
    request_data = {
        "business": business,
        "matches": requirements
    }
    
    response = client.post("/api/report", json=request_data)
    
    # Should return 200 (or 400/500 if report generation fails, but not 422)
    assert response.status_code in [200, 400, 500]
    if response.status_code == 200:
        data = response.json()
        assert "report" in data

def test_api_report_endpoint_with_requirements_alias():
    """Test /api/report endpoint with 'requirements' field (backward compatibility)"""
    business = {
        "business_name": "Test Business",
        "size": "small",
        "seats": 10,
        "area_sqm": 50,
        "staff_count": 2,
        "features": ["gas"]
    }
    
    requirements = [
        {
            "id": "req1",
            "title": "Test Requirement",
            "category": "Test",
            "priority": "High",
            "description": "Test description"
        }
    ]
    
    request_data = {
        "business": business,
        "requirements": requirements
    }
    
    response = client.post("/api/report", json=request_data)
    
    # Should return 200 (or 400/500 if report generation fails, but not 422)
    assert response.status_code in [200, 400, 500]
    if response.status_code == 200:
        data = response.json()
        assert "report" in data

def test_api_report_endpoint_validation_error():
    """Test /api/report endpoint returns 422 for invalid payload"""
    business = {
        "business_name": "Test Business",
        "size": "small",
        "seats": 10,
        "area_sqm": 50,
        "staff_count": 2,
        "features": ["gas"]
    }
    
    # Missing 'matches'/'requirements' field
    request_data = {
        "business": business
    }
    
    response = client.post("/api/report", json=request_data)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_api_report_endpoint_malformed_business():
    """Test /api/report endpoint returns 422 for malformed business data"""
    business = {
        "business_name": "Test Business",
        "size": "invalid_size",  # Invalid size
        "seats": 10,
        "area_sqm": 50,
        "staff_count": 2,
        "features": ["gas"]
    }
    
    requirements = [
        {
            "id": "req1",
            "title": "Test Requirement",
            "category": "Test",
            "priority": "High",
            "description": "Test description"
        }
    ]
    
    request_data = {
        "business": business,
        "matches": requirements
    }
    
    response = client.post("/api/report", json=request_data)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_api_report_endpoint_malformed_requirements():
    """Test /api/report endpoint returns 422 for malformed requirements data"""
    business = {
        "business_name": "Test Business",
        "size": "small",
        "seats": 10,
        "area_sqm": 50,
        "staff_count": 2,
        "features": ["gas"]
    }
    
    requirements = [
        {
            "id": "req1",
            "title": "Test Requirement",
            "category": "Test",
            "priority": "InvalidPriority",  # Invalid priority
            "description": "Test description"
        }
    ]
    
    request_data = {
        "business": business,
        "matches": requirements
    }
    
    response = client.post("/api/report", json=request_data)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
