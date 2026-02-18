@echo off
echo ========================================
echo   ExpenseAI SaaS Platform Startup
echo ========================================
echo.

echo [1/4] Creating test users...
cd backend
python create_test_users.py
echo.

echo [2/4] Starting backend server...
start cmd /k "cd backend && uvicorn main:app --reload"
timeout /t 3 /nobreak > nul
echo Backend started on http://localhost:8000
echo.

echo [3/4] Starting frontend server...
start cmd /k "cd frontend && npm start"
timeout /t 3 /nobreak > nul
echo Frontend starting on http://localhost:3000
echo.

echo [4/4] Opening browser...
timeout /t 5 /nobreak > nul
start http://localhost:3000
echo.

echo ========================================
echo   SaaS Platform is Running!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
echo Test Accounts:
echo   FREE: free@test.com / password123
echo   PRO: pro@test.com / password123
echo   ADMIN: admin@test.com / password123
echo.
echo Press any key to stop all servers...
pause > nul

echo.
echo Stopping servers...
taskkill /F /FI "WINDOWTITLE eq *uvicorn*" > nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *npm*" > nul 2>&1
echo Servers stopped.
echo.
pause
