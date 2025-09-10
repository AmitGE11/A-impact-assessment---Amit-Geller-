import os
import logging
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json
from pathlib import Path

from models import BusinessInput, MatchResponse, ReportRequest, ReportResponse
from services.matcher import match_requirements
from services.report import generate_report

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Licensure Buddy IL", version="1.0.0")

# CORS configuration
origins = ["http://localhost:5500","http://127.0.0.1:5500","http://localhost:5173","http://127.0.0.1:5173","*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Load requirements data
def load_requirements():
    # Try to load parsed requirements first, fallback to sample data
    parsed_path = Path(__file__).parent / "data" / "requirements.json"
    sample_path = Path(__file__).parent / "data" / "requirements.sample.json"
    
    if parsed_path.exists():
        try:
            with open(parsed_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} requirements from {parsed_path.name}")
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    # Fallback to sample data
    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} requirements from {sample_path.name}")
            return data
    except FileNotFoundError:
        logger.warning("No requirements data found")
        return []

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/api/requirements")
async def get_requirements():
    """Get all requirements from sample data"""
    requirements = load_requirements()
    return requirements

@app.post("/api/match", response_model=MatchResponse)
async def match_business_requirements(business: BusinessInput):
    """Match business profile against requirements"""
    try:
        requirements = load_requirements()
        matched = match_requirements(business, requirements)
        
        # Log the count and which data file was used
        data_file = "requirements.json" if (Path(__file__).parent / "data" / "requirements.json").exists() else "requirements.sample.json"
        logger.info(f"Matched {len(matched)} requirements for business (size={business.size}, seats={business.seats}, area={business.area_sqm}, staff={business.staff_count}, features={len(business.features)}) using {data_file}")
        
        return MatchResponse(business=business, matched=matched)
    except Exception as e:
        logger.error(f"Error matching business requirements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/report", response_model=ReportResponse)
async def generate_business_report(request: ReportRequest):
    """Generate AI-powered compliance report"""
    try:
        report_text = generate_report(request)
        return ReportResponse(report=report_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
