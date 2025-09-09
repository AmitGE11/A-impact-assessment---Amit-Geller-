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

# Copy environment file (optional: add your OpenAI API key)
cp env.example .env

# Start development server
bash run_dev.sh
```

The backend will be available at `http://localhost:8000`

### 2. Open Frontend

Open `frontend/index.html` in your web browser.

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

- **Step 1**: Currently uses sample data from `requirements.sample.json`
- **Step 2**: Next phase will parse actual requirements from provided PDF/Word documents
- **AI Integration**: Falls back to structured mock reports when OpenAI API key is not provided
- **CORS**: Configured to allow all origins in development

## License

This project is part of the Israeli business licensing assessment initiative.

---

*Built with ❤️ for Israeli businesses*
