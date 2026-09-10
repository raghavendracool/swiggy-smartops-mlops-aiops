# Swiggy SmartOps - Run Guide

This guide contains the exact commands to run backend, frontend, and Streamlit dashboard locally on Windows PowerShell.

## 1) Open project root

```powershell
cd "C:\Users\RaghavendraRao\OneDrive - NewVision Software Pvt.Ltd\Trainings\Git\swiggy-smartops-mlops-aiops"
```

## 2) Activate virtual environment

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

## 3) Install dependencies

### Python dependencies

```powershell
pip install -r requirements.txt
```

If requirements encoding causes an error, run:

```powershell
Get-Content requirements.txt -Encoding Unicode | Set-Content requirements.utf8.txt -Encoding UTF8
pip install -r requirements.utf8.txt
```

### Frontend dependencies

```powershell
cd .\frontend
npm install
cd ..
```

## 4) Run services (use separate terminals)

### Terminal 1 - FastAPI backend

```powershell
cd "C:\Users\RaghavendraRao\OneDrive - NewVision Software Pvt.Ltd\Trainings\Git\swiggy-smartops-mlops-aiops"
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URLs:
- Health: http://127.0.0.1:8000/health
- API Docs: http://127.0.0.1:8000/docs

### Terminal 2 - React frontend (Vite)

```powershell
cd "C:\Users\RaghavendraRao\OneDrive - NewVision Software Pvt.Ltd\Trainings\Git\swiggy-smartops-mlops-aiops\frontend"
npm run dev
```

Frontend URL:
- Local: http://localhost:5173/

### Terminal 3 - Streamlit MLOps dashboard

From project root:

```powershell
cd "C:\Users\RaghavendraRao\OneDrive - NewVision Software Pvt.Ltd\Trainings\Git\swiggy-smartops-mlops-aiops"
.\.venv\Scripts\Activate.ps1
python -m streamlit run app/app.py --server.address 127.0.0.1 --server.port 8501
```

Dashboard URL:
- Local: http://localhost:8501

If port 8501 is unavailable:

```powershell
python -m streamlit run app/app.py --server.address 127.0.0.1 --server.port 8502
```

## 5) Quick checks

### Backend check

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### Frontend build/lint checks

```powershell
cd .\frontend
npm run lint
npm run build
```

## 6) One-command startup (optional)

If using the helper script:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-all.ps1
```

Only Streamlit dashboard:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-all.ps1 -NoBackend -NoFrontend
```
