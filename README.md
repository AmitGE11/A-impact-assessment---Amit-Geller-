# Licensure Buddy IL

מערכת סיוע לרישוי עסקים בישראל | Israeli Business Licensing Assistant

A production-ready FastAPI + vanilla JavaScript application that helps Israeli businesses understand their licensing requirements through AI-powered analysis.

## Features

- **Business Profile Matching**: Match business characteristics against licensing requirements
- **AI-Powered Reports**: Generate detailed compliance reports in Hebrew
- **Sample Data**: Pre-loaded with representative Israeli business licensing requirements
- **RTL Support**: Full Hebrew language support with right-to-left layout

## Tech Stack

- **Backend**: Python 3.11 + FastAPI + Uvicorn
- **Frontend**: Vanilla HTML/CSS/JavaScript (no build process)
- **Data**: JSON files in `./backend/data`
- **AI Integration**: OpenAI API (with fallback to mock reports)
- **CORS**: Enabled for cross-origin requests

## Quick Start

### 1. Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Optional: generate structured data from the PDF
python process_pdf.py      # uses backend/data/18-07-2022_4.2A.pdf

# Copy environment file (optional: add your OpenAI API key)
cp env.example .env

# Start development server
bash run_dev.sh
```

The backend will be available at `http://localhost:8000`

### 2. Open Frontend

Open `frontend/index.html` in your web browser.

## Using the Questionnaire

The digital questionnaire supports comprehensive business feature selection:

### Numeric Fields
- **שטח העסק (מ״ר)**: Business area in square meters
- **מספר עובדים במשמרת**: Number of staff per shift

### Feature Categories
- **Basic Features**: גז, בשר, משלוחים
- **Service Features**: הגשת אלכוהול, ישיבה חיצונית, מוסיקה/בידור, אזור עישון, פתוח אחרי חצות, איסוף עצמי
- **Kitchen Features**: מטבח חם, מטבח קר בלבד, מזון חלבי, מזון דגים, טבעוני
- **Safety Features**: מלכודת שומן, מנדף/יניקה, מטפי כיבוי ניידים, מערכת מתזים/ספרינקלרים, עמדות שטיפת ידיים, בדיקת גז בתוקף
- **Operations Features**: קירור מסחרי, מקפיא/הקפאה, הצהרת אלרגנים בתפריט, נגישות לנכים, רישיון ושילוט במקום בולט, הדברה תקופתית, הפרדת פסולת/שמן בישול

### Matching Logic
The matching system supports multiple condition types:
- **Thresholds**: min/max seats, min/max area (sqm), min/max staff count
- **Feature Logic**: `features_any`, `features_all`, `features_none` conditions
- **Size Logic**: `size_any` for business size matching

This comprehensive approach ensures accurate requirement matching based on your complete business profile.

## Pushing Code

This repository uses the `main` branch as the default. Use the provided helper scripts to safely sync your changes:

### Windows (PowerShell)
```powershell
# Quick sync with default message
./sync-main.ps1

# Sync with custom commit message
./sync-main.ps1 "feat: add new feature"
```

### macOS/Linux (bash)
```bash
# Quick sync with default message
bash tools/git_sync_main.sh

# Sync with custom commit message
bash tools/git_sync_main.sh "feat: add new feature"
```

### What the scripts do:
- Rename local `master` branch to `main` if needed
- Set `main` as the default branch for future repositories
- Pull latest changes from remote `main` branch
- Stage and commit all local changes
- Push to `origin/main` with upstream tracking

**Note**: If a pull request is required, use the GitHub UI after pushing.

## API Endpoints

### Health Check
```bash
GET /api/health
# Response: {"status": "ok"}
```

### Get Requirements
```bash
GET /api/requirements
# Response: Array of requirement objects
```

### Match Business Requirements
```bash
POST /api/match
Content-Type: application/json

{
  "size": "small|medium|large",
  "seats": 50,
  "features": ["gas", "meat", "delivery"]
}

# Response: {"business": {...}, "matched": [...]}
```

### Generate Report
```bash
POST /api/report
Content-Type: application/json

{
  "business": {
    "size": "medium",
    "seats": 50,
    "features": ["gas"]
  },
  "requirements": [...]
}

# Response: {"report": "Hebrew compliance report..."}
```

## Environment Variables

Create a `.env` file in the `backend` directory:

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini
PORT=8000
HOST=0.0.0.0
ALLOWED_ORIGINS=*
```

## Project Structure

```
.
├── README.md
├── .gitignore
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Pydantic models
│   ├── services/
│   │   ├── matcher.py          # Business-requirements matching logic
│   │   ├── report.py           # AI report generation
│   │   └── __init__.py
│   ├── data/
│   │   ├── requirements.sample.json  # Sample licensing requirements
│   │   ├── requirements.json         # Generated from PDF (via process_pdf.py)
│   │   ├── 18-07-2022_4.2A.pdf      # Source PDF document
│   │   └── README.md
│   ├── requirements.txt
│   ├── env.example
│   └── run_dev.sh
└── frontend/
    ├── index.html              # Main application page
    ├── app.js                  # Frontend JavaScript
    └── styles.css              # Styling
```

## Development Notes

- **Step 1**: Data processing pipeline complete - PDF parsed to structured JSON
- **Data Sources**: 
  - `requirements.sample.json` - Demo data for initial testing
  - `requirements.json` - Generated from PDF via `process_pdf.py`
- **AI Integration**: Falls back to structured mock reports when OpenAI API key is not provided
- **CORS**: Configured to allow all origins in development

### Step 1 — Data Processing (PDF → JSON, relative paths)

I implemented a reproducible data pipeline that converts the provided regulatory PDF into structured JSON using a relative-path workflow. The script `backend/process_pdf.py` (pdfplumber-based) reads `backend/data/18-07-2022_4.2A.pdf`, cleans the text, splits it into requirement blocks with a simple heuristic, and writes `backend/data/requirements.json`. Each item includes: `id`, `category`, `title`, `description`, `priority`, and `conditions` (size/seats/features). The backend now prefers `requirements.json` when present and falls back to `requirements.sample.json`, ensuring the app runs locally for any reviewer without hardcoded machine-specific paths.

## License

This project is part of the Israeli business licensing assessment initiative.

---

*Built with ❤️ for Israeli businesses*
