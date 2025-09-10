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

Open `frontend/index.html` in your web browser (using Live Server or similar).

**Note**: If the backend uses a different port, click "הגדר כתובת שרת" (Set API Base) on the page and enter the URL (e.g., `http://localhost:8080`).

### 3. Health Check

The application automatically checks the backend health on page load:
- **השרת פעיל** (Server Active) - Backend is running
- **השרת לא זמין** (Server Unavailable) - Backend is not accessible

Health endpoint: `/api/health`

## How to Enable AI Report

The application can generate AI-powered compliance reports using OpenAI's API. Without an API key, it falls back to a deterministic mock report.

### 1. Get OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy the key (starts with `sk-`)

### 2. Configure Environment

1. Navigate to the `backend` directory
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Edit `backend/.env` and add your API key:
   ```
   OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXX
   OPENAI_MODEL=gpt-4o-mini
   ```

### 3. Optional Model Configuration

You can change the AI model by modifying `OPENAI_MODEL` in `.env`:
- `gpt-4o-mini` (default, cost-effective)
- `gpt-4o` (more capable)
- `gpt-3.5-turbo` (legacy, cheaper)

### 4. Test AI Integration

1. Start the backend server
2. Open the frontend
3. Fill out the business questionnaire
4. Generate a report
5. Look for the model badge showing "מודל בשימוש: gpt-4o-mini" (or your selected model)

### 5. Mock Mode

If no API key is provided or the API fails, the application automatically falls back to mock mode:
- Shows "מודל בשימוש: Mock" badge
- Generates a structured Hebrew report based on matched requirements
- No external API calls are made

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

## Matching Engine

The matching engine provides intelligent rule-based matching with detailed explanations for each requirement match.

### Inputs Considered

The matching engine evaluates business profiles based on:

- **Business Size**: `small`, `medium`, or `large`
- **Seating Capacity**: Number of seats (integer)
- **Area**: Business area in square meters (integer)
- **Staff Count**: Number of staff per shift (integer)
- **Features**: List of business features (array of strings)

### Supported Conditions

The engine supports comprehensive condition matching:

#### Size Conditions
- **`size_any`**: Business size must be in the specified list
  - Example: `{"size_any": ["medium", "large"]}`

#### Numeric Conditions
- **`min_seats`**: Minimum seating requirement
- **`max_seats`**: Maximum seating limit
- **`min_area_sqm`**: Minimum area requirement (square meters)
- **`max_area_sqm`**: Maximum area limit (square meters)
- **`min_staff`**: Minimum staff requirement
- **`max_staff`**: Maximum staff limit

#### Feature Conditions
- **`features_any`**: Business must have at least one of the specified features
- **`features_all`**: Business must have all of the specified features
- **`features_none`**: Business must not have any of the specified features

#### General Rules
- Rules with no conditions match all businesses (general requirements)

### Output with Explanations

Each matched requirement includes detailed explanations (`reasons`) that explain why the rule matched:

- **Size matches**: "סוג העסק 'medium' נכלל ב-size_any"
- **Numeric matches**: "50≥30 ⇒ min_seats", "שטח 100≥50 ⇒ min_area_sqm"
- **Feature matches**: "מאפיין כלשהו מזוהה: ['alcohol']", "כל המאפיינים הדרושים קיימים: ['gas', 'meat']"
- **General rules**: "כללי — ללא תנאים"

### Sorting

Results are automatically sorted by:
1. **Priority**: High → Medium → Low
2. **Category**: Alphabetical order
3. **Title**: Alphabetical order

This ensures the most critical requirements appear first, making it easier for business owners to prioritize their compliance efforts.

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

#### Better parsing for Hebrew PDFs

The improved parser now supports:
- **Multi-library extraction**: pdfminer.six → pdfplumber → python-docx fallback chain
- **RTL text handling**: Uses python-bidi to fix Hebrew text display order
- **Numbered clause splitting**: Detects numbered headings (e.g., "3.1.2", "4.5.6.7") and bullet points
- **Automatic condition extraction**: Heuristically mines conditions from text using regex patterns:
  - Seats: "עד X מקומות" → max_seats, "מעל X מקומות" → min_seats
  - Area: "עד X מ״ר" → max_area_sqm, "מעל X מ״ר" → min_area_sqm
  - Staff: "X עובדים" → min_staff (when "נדרשים" is present)
  - Features: Keyword detection for gas, meat, dairy, alcohol, etc.
- **Smart deduplication**: Removes near-identical blocks based on title similarity
- **Priority inference**: High for "חובה/נדרש", Medium for "מומלץ", Low otherwise

**Applied Hebrew BiDi normalization to all lines (python-bidi), normalized parentheses, removed dotted rulers, and ensured non-empty titles with a robust fallback.**

## License

This project is part of the Israeli business licensing assessment initiative.

---

*Built with ❤️ for Israeli businesses*
