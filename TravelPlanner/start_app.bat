@echo off
echo 🧳 Travel Planner App - Starting Services
echo ========================================

echo.
echo 🚀 Starting Backend API...
start "Backend API" cmd /k "python start_backend.py"

echo.
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo 🎨 Starting Frontend UI...
start "Frontend UI" cmd /k "python start_frontend.py"

echo.
echo ✅ Both services are starting!
echo.
echo 📍 Backend API: http://localhost:8000
echo 📍 Frontend UI: http://localhost:8501
echo.
echo Press any key to exit...
pause > nul
