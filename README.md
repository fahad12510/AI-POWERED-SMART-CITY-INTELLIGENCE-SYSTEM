# AI-Powered Smart City Intelligence System

A student-friendly Flask application that analyzes fictional traffic and Air Quality Index (AQI) readings using NumPy, visualizes them with Chart.js, estimates simple trends, flags unusual readings, and optionally uses Groq for natural-language explanations.

## Important data note
The included Rawalpindi-area location names and values are an educational sample dataset. They are fictional and are **not live measurements**. Do not use this project for real traffic, environmental, or public-health decisions.

## Features
- Flask JSON API and responsive dashboard
- NumPy statistics, ranking, vectorized percentage changes, broadcasting growth scenario and boolean anomaly masks
- Linear next-day trend estimates using `numpy.polyfit`
- CSV upload validation; missing location/day records are rejected, not silently filled with zero
- Groq AI analysis, recommendations and question answering
- Clearly labelled demo responses when Groq credentials are unavailable
- PDF report generation

## Windows setup
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `.env` and add your Groq API key and a currently supported model ID from your Groq account. Leave them blank to use Demo Mode.

Run:
```powershell
py app.py
```
Open http://127.0.0.1:5000

## CSV format
Required columns: `location,day,traffic,aqi`. Each location must have one reading for every day represented in the file. Values must be numeric, finite and non-negative. Files are limited to 2 MB.

## API routes
- `GET /api/dashboard`
- `GET /api/traffic`
- `GET /api/air-quality`
- `GET /api/analytics`
- `GET /api/predictions`
- `POST /api/upload-dataset`
- `POST /api/restore-sample`
- `POST /api/ai/analyze`
- `POST /api/ai/ask`
- `POST /api/ai/recommendations`
- `POST /api/ai/explain`
- `POST /api/ai/generate-report`

## Testing checklist
1. Start the app and verify the dashboard.
2. Confirm Demo Mode with empty `.env` credentials.
3. Upload a valid CSV and then an incomplete CSV.
4. Restore the sample dataset.
5. Generate a PDF report.
6. Add valid Groq credentials and test AI features.

## GitHub
```powershell
git init
git add .
git commit -m "Initial Smart City Intelligence System"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```
Never commit `.env` or real API keys.

## Deployment notes
For a conventional Flask host such as Render, configure the start command (for example `gunicorn app:app`) and set `GROQ_API_KEY` and `GROQ_MODEL` in the host's environment settings. Add `gunicorn` to requirements for that deployment. Local uploaded CSVs are stored on disk and may be lost on ephemeral hosting; use persistent disks or object/database storage if uploads must survive restarts.

## Limitations
The prediction is a straight-line fit to only seven readings. Anomaly flags are prompts for human review, not proof of emergencies. Demo AI text is predefined and is never represented as a live model response.
