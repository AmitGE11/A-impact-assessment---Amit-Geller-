Here’s your **rewritten README.md**, fully aligned with the assignment instructions and updated to **Gemini** (no more OpenAI references).

---

# Licensure Buddy IL

מערכת סיוע לרישוי עסקים בישראל | Israeli Business Licensing Assistant

A FastAPI + vanilla JavaScript application that helps Israeli businesses understand their licensing requirements through AI-powered analysis.

---

## Project Goals

* Parse raw regulatory data (PDF/Word) into structured JSON
* Collect business information through a digital questionnaire
* Match business characteristics against licensing requirements
* Generate AI-powered compliance reports in Hebrew using **Gemini**

---

## Installation & Run

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Optional: parse the provided PDF into JSON
python process_pdf.py

# Copy environment variables
cp env.example .env
```

Run:

```bash
bash run_dev.sh
```

Backend available at: `http://localhost:8000`

### 2. Frontend

Open `frontend/index.html` in your browser (Live Server recommended).
If backend runs on a different port, set it using "הגדר כתובת שרת" in the UI.

---

## Dependencies

* Python 3.11
* FastAPI, Uvicorn
* pdfplumber (for parsing PDF)
* Google Generative AI Python SDK (Gemini)
* Vanilla HTML/CSS/JS (frontend)

See `backend/requirements.txt` for full versions.

---

## System Architecture

```
Frontend (HTML/JS)  <──►  Backend API (FastAPI/Python)  <──►  Data (JSON)
                                               │
                                               └──► AI API (Gemini)
```

---

## API Endpoints

* `GET /api/health` → `{"status": "ok"}`
* `GET /api/requirements` → Array of requirement objects
* `POST /api/match` → Match business profile to requirements
* `POST /api/report` → Generate compliance report (AI or mock)

---

## Data Schema

Each requirement record:

```json
{
  "id": "req-001",
  "category": "Safety",
  "title": "Fire Safety Approval",
  "description": "Obtain fire safety certificate.",
  "priority": "High",
  "conditions": {
    "min_seats": 30,
    "features_any": ["gas", "meat"]
  }
}
```

---

## Matching Logic

* **Size filters**: small / medium / large
* **Numeric thresholds**: min/max seats, area, staff
* **Feature logic**: must include/exclude certain features
* **Priority sorting**: High → Medium → Low

---

## AI Integration

* **Model**: `gemini-1.5-flash` (default, fast and cost-effective)
* **Why**: strong Hebrew support, good balance between accuracy and latency
* **Fallback**: if no API key, system generates structured mock reports

### Example Prompt

```text
Analyze the following business profile and regulatory requirements.
Summarize in Hebrew a compliance report, grouped by category,
with clear priorities and recommendations.
```

### Environment Variables

In `backend/.env`:

```env
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-1.5-flash
```

---

## Screenshots

(Attach 2–3 screenshots of questionnaire, results, and AI report.)

---

✨ Keep the README clean and focused for the assignment.
For extra details (parsing methods, dev scripts, future improvements), create a `DEVELOPMENT_NOTES.md`.

---

Do you also want me to **rewrite the `.env.example` file** to match Gemini (instead of OpenAI)?
