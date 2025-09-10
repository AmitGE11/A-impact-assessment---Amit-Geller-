from pathlib import Path
from dotenv import load_dotenv, dotenv_values

ENV_PATH = Path(__file__).resolve().parent / ".env"
# Force UTF-8 and override
load_dotenv(ENV_PATH, override=True, encoding="utf-8")

# If PROVIDER is still empty, parse and inject manually
import os
if not (os.getenv("PROVIDER") or "").strip():
    vals = dotenv_values(ENV_PATH)
    os.environ.update({k:str(v) for k,v in vals.items() if v is not None})

import logging
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log which env file was loaded
logging.getLogger("main").info("Loaded env file: %s", ENV_PATH)
logging.getLogger("main").info("Startup provider: %s", os.getenv("PROVIDER") or "<unset>")

from models import BusinessInput, MatchResponse, ReportRequest, ReportResponse
from services.matcher import match_requirements
from services.report import generate_report

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

@app.get("/api/ai/status")
def ai_status():
    provider = (os.getenv("PROVIDER") or "mock").lower()
    return {"provider": provider}

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
def report(req: ReportRequest):
    try:
        data = generate_report(req.business, req.matches)
        return ReportResponse(**data)
    except Exception:
        logging.getLogger("main").exception("Report generation failed")
        raise HTTPException(status_code=500, detail="AI report generation failed")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
