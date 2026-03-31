@echo off
echo.
echo ==============================================================
echo   Installing Missing Python Dependencies
echo ==============================================================
echo.

cd /d "%~dp0"

echo [1/2] Installing scikit-learn...
pip install scikit-learn==1.3.2
if errorlevel 1 (
    echo ERROR: Failed to install scikit-learn
    pause
    exit /b 1
)
echo OK: scikit-learn installed
echo.

echo [2/2] Installing langchain packages...
pip install langchain-openai==0.2.1 langchain-core==0.3.10 langchain-community==0.3.5 langchain-huggingface==0.1.0
if errorlevel 1 (
    echo ERROR: Failed to install langchain packages
    pause
    exit /b 1
)
echo OK: langchain packages installed
echo.

echo ==============================================================
echo   Installation Complete!
echo ==============================================================
echo.
echo You can now run the verification again:
echo   verify.bat
echo.
pause
