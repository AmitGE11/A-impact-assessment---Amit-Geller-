from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field

class BusinessInput(BaseModel):
    """Business profile input for matching requirements"""
    size: Literal["small", "medium", "large"]
    seats: int = Field(ge=0, description="Number of seats")
    features: List[str] = Field(default_factory=list, description="Business features")

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
