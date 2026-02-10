@echo off
echo Installing authentication dependencies...
python -m pip install bcrypt python-jose[cryptography] passlib python-multipart

echo.
echo Removing old database...
if exist expenses.db del expenses.db

echo.
echo Setup complete! Now run: python -m uvicorn main:app --reload
pause
