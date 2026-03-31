@echo off
echo.
echo ==============================================================
echo      TELECONTROL DEPLOYMENT VERIFICATION
echo ==============================================================
echo.

cd /d "%~dp0"

echo [1/9] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo OK: Python is installed
echo.

echo [2/9] Checking .env file...
if exist .env (
    echo OK: .env file exists
) else (
    echo WARNING: .env file not found!
)
echo.

echo [3/9] Checking ML model files...
if exist classificador_defeitos.pkl (
    echo OK: classificador_defeitos.pkl found
) else (
    echo WARNING: classificador_defeitos.pkl not found
)
echo.

echo [4/9] Checking DATASET folder...
if exist DATASET (
    echo OK: DATASET folder exists
    dir /b DATASET\*.csv 2>nul
) else (
    echo WARNING: DATASET folder not found!
)
echo.

echo [5/9] Checking frontend folder...
if exist telecon-ai (
    echo OK: telecon-ai folder exists
) else (
    echo ERROR: telecon-ai folder not found!
)
echo.

echo [6/9] Running Python verification script...
python verify_deployment.py

echo.
echo ==============================================================
echo                   VERIFICATION COMPLETE
echo ==============================================================
echo.
echo Next steps:
echo 1. Review the results above
echo 2. Fix any errors or warnings
echo 3. Test your deployment at: https://telecontrol-ai.vercel.app
echo.
pause
