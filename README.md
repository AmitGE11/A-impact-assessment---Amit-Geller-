
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
GEMINI_API_KEY=AIzaSyCe6--2MV2s9YCVvSeCSKzBG69dEd6G34o
GEMINI_MODEL=gemini-1.5-flash
```

---

## Screenshots

<img width="1052" height="654" alt="Screenshot 2025-09-12 074553" src="https://github.com/user-attachments/assets/86a6983d-8361-4c06-b5b4-8e0adc4a2acc" />
<img width="1078" height="857" alt="Screenshot 2025-09-12 074612" src="https://github.com/user-attachments/assets/b3e814c1-d508-4b4b-b5df-c29e89ed56f6" />
<img width="843" height="878" alt="Screenshot 2025-09-12 074638" src="https://github.com/user-attachments/assets/518df2e6-6d71-4438-a718-074f68449cff" />

---

This Project of The A-Impact Appliction Process 
