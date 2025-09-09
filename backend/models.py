from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

# Allowed business features
ALLOWED_FEATURES = {
    "gas", "meat", "delivery", "alcohol", "outdoor", "music", "smoking",
    "kitchen_hot", "kitchen_cold", "dairy", "fish", "vegan", "night", "takeaway",
    "grease_trap", "hood_vent", "fire_ext", "sprinkler", "handwash", "refrigeration",
    "freezer", "allergen_note", "accessibility", "signage", "pest_control", "waste_sep", "gas_cert"
}

class BusinessInput(BaseModel):
    """Business profile input for matching requirements"""
    size: Literal["small", "medium", "large"]
    seats: int = Field(ge=0, description="Number of seats")
    area_sqm: Optional[int] = Field(default=0, ge=0, description="Business area in square meters")
    staff_count: Optional[int] = Field(default=0, ge=0, description="Number of staff per shift")
    features: List[str] = Field(default_factory=list, description="Business features")
    
    @validator('features')
    def validate_features(cls, v):
        """Validate that all features are in the allowed list"""
        invalid_features = set(v) - ALLOWED_FEATURES
        if invalid_features:
            raise ValueError(f"תכונות לא מורשות: {', '.join(invalid_features)}. תכונות מורשות: {', '.join(sorted(ALLOWED_FEATURES))}")
        return v

class RequirementItem(BaseModel):
    """Individual requirement item"""
    id: str
    title: str
    category: str
    priority: Literal["High", "Medium", "Low"]
    description: str
    conditions: Dict[str, Any] = Field(default_factory=dict)

class MatchResponse(BaseModel):
    """Response for business-requirements matching"""
    business: BusinessInput
    matched: List[RequirementItem]

class ReportRequest(BaseModel):
    """Request for generating compliance report"""
    business: BusinessInput
    requirements: List[RequirementItem]

class ReportResponse(BaseModel):
    """Response containing generated report"""
    report: str
