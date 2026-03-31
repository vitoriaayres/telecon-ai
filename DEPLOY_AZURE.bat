@echo off
REM ============================================================
REM TeleControl Deployment Script for Azure App Service
REM ============================================================
REM This script automates deployment to Azure (Brazil South)
REM Prerequisites: Docker, Azure CLI, Node.js, Git
REM ============================================================

setlocal enabledelayedexpansion

REM Color codes
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  TELECONTROL AZURE APP SERVICE DEPLOYMENT SCRIPT           ║
echo ║  Target: Brazil South Region                              ║
echo ║  Status: Ready to Deploy                                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Configuration
set APP_NAME=telecontrol
set RESOURCE_GROUP=telecontrol-rg
set REGION=brazilsouth
set BACKEND_APP_NAME=telecontrol-api
set FRONTEND_APP_NAME=telecontrol-web
set PLAN_NAME=telecontrol-plan
set REGISTRY_NAME=telecontrolregistry
set SKU=F1
set AZ_CMD=az
set "AZ_FALLBACK=C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

REM Azure Credentials (set in environment or here)
set AZURE_OPENAI_ENDPOINT=https://breakfixtesteunimar.cognitiveservices.azure.com/
set AZURE_OPENAI_API_KEY=<SUA_CHAVE_AZURE_OPENAI>
set AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1-mini-2
set AZURE_OPENAI_API_VERSION=2024-08-01-preview

echo.
echo [STEP 1/8] Checking Prerequisites...
echo ══════════════════════════════════════════════════════════════

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Docker not found! Please install Docker Desktop
    exit /b 1
)
echo ✓ Docker installed

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Node.js not found! Please install Node.js 18+
    exit /b 1
)
echo ✓ Node.js installed

REM Check Azure CLI
if exist "%AZ_FALLBACK%" (
    set "AZ_CMD=%AZ_FALLBACK%"
)

"%AZ_CMD%" --version >nul 2>&1
if %errorlevel% neq 0 (
    az --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ✗ Azure CLI not found in PATH and fallback path failed
        echo   Install Azure CLI or add it to PATH: C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin
        exit /b 1
    )
    set "AZ_CMD=az"
)
echo ✓ Azure CLI installed

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Git not found! Please install Git
    exit /b 1
)
echo ✓ Git installed

echo.
echo [STEP 2/8] Checking Azure Authentication...
echo ══════════════════════════════════════════════════════════════

"%AZ_CMD%" account show >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Not logged into Azure. Running: az login
  call "%AZ_CMD%" login
)
echo ✓ Azure authenticated

echo.
echo [STEP 3/8] Creating Azure Resources...
echo ══════════════════════════════════════════════════════════════

REM Create Resource Group
echo Creating resource group...
call "%AZ_CMD%" group create ^
  --name %RESOURCE_GROUP% ^
  --location %REGION% ^
  --output none 2>nul
echo ✓ Resource group ready

REM Create App Service Plan
echo Creating app service plan...
call "%AZ_CMD%" appservice plan create ^
  --name %PLAN_NAME% ^
  --resource-group %RESOURCE_GROUP% ^
  --location %REGION% ^
  --is-linux ^
  --sku %SKU% ^
  --output none 2>nul
echo ✓ App Service plan ready

echo.
echo [STEP 4/8] Building Backend...
echo ══════════════════════════════════════════════════════════════

cd /d "C:\Users\Interfocus\Desktop\UNIMAR\telecontrol"

REM Build Docker image
echo Building Docker image...
call docker build -t %BACKEND_APP_NAME%:latest . >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Docker build failed!
    exit /b 1
)
echo ✓ Docker image built

echo.
echo [STEP 5/8] Creating Backend Web App...
echo ══════════════════════════════════════════════════════════════

call "%AZ_CMD%" webapp create ^
  --resource-group %RESOURCE_GROUP% ^
  --plan %PLAN_NAME% ^
  --name %BACKEND_APP_NAME% ^
  --runtime "PYTHON:3.11" ^
  --output none 2>nul
echo ✓ Backend web app created

REM Configure app settings
echo Configuring backend environment variables...
call "%AZ_CMD%" webapp config appsettings set ^
  --name %BACKEND_APP_NAME% ^
  --resource-group %RESOURCE_GROUP% ^
  --settings ^
    AZURE_OPENAI_ENDPOINT="%AZURE_OPENAI_ENDPOINT%" ^
    AZURE_OPENAI_API_KEY="%AZURE_OPENAI_API_KEY%" ^
    AZURE_OPENAI_DEPLOYMENT_NAME="%AZURE_OPENAI_DEPLOYMENT_NAME%" ^
    AZURE_OPENAI_API_VERSION="%AZURE_OPENAI_API_VERSION%" ^
    WEBSITES_PORT=8000 ^
  --output none 2>nul
echo ✓ Environment variables configured

echo.
echo [STEP 6/8] Building Frontend...
echo ══════════════════════════════════════════════════════════════

cd /d "C:\Users\Interfocus\Desktop\UNIMAR\telecontrol\telecon-ai"

echo Running npm install...
call npm install --silent >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ npm install failed!
    exit /b 1
)
echo ✓ Dependencies installed

echo Running npm build...
call npm run build >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ npm build failed!
    exit /b 1
)
echo ✓ Frontend built

echo.
echo [STEP 7/8] Creating Frontend Web App...
echo ══════════════════════════════════════════════════════════════

call "%AZ_CMD%" webapp create ^
  --resource-group %RESOURCE_GROUP% ^
  --plan %PLAN_NAME% ^
  --name %FRONTEND_APP_NAME% ^
  --runtime "NODE:20-lts" ^
  --output none 2>nul
echo ✓ Frontend web app created

REM Configure frontend settings
echo Configuring frontend environment variables...
call "%AZ_CMD%" webapp config appsettings set ^
  --name %FRONTEND_APP_NAME% ^
  --resource-group %RESOURCE_GROUP% ^
  --settings ^
    BACKEND_URL="https://%BACKEND_APP_NAME%.azurewebsites.net" ^
  --output none 2>nul
echo ✓ Frontend configured

echo.
echo [STEP 8/8] Deploying Applications...
echo ══════════════════════════════════════════════════════════════

cd /d "C:\Users\Interfocus\Desktop\UNIMAR\telecontrol"

echo Deploying backend...
call "%AZ_CMD%" webapp deployment source config-zip ^
  --resource-group %RESOURCE_GROUP% ^
  --name %BACKEND_APP_NAME% ^
  --src telecontrol.zip >nul 2>&1
echo ✓ Backend deployed

cd /d "C:\Users\Interfocus\Desktop\UNIMAR\telecontrol\telecon-ai"

echo Deploying frontend...
call "%AZ_CMD%" webapp deployment source config-zip ^
  --resource-group %RESOURCE_GROUP% ^
  --name %FRONTEND_APP_NAME% ^
  --src frontend.zip >nul 2>&1
echo ✓ Frontend deployed

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  ✓ DEPLOYMENT COMPLETE!                                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Your applications are now live!
echo.
echo 🌐 FRONTEND:  https://%FRONTEND_APP_NAME%.azurewebsites.net
echo 🔗 BACKEND:   https://%BACKEND_APP_NAME%.azurewebsites.net
echo 📊 HEALTH:    https://%BACKEND_APP_NAME%.azurewebsites.net/health
echo.
echo Next steps:
echo 1. Wait 2-3 minutes for apps to start
echo 2. Visit the frontend URL to test
echo 3. Check logs in Azure Portal if issues occur
echo.
echo To view logs:
echo   az webapp log tail -n 50 -g %RESOURCE_GROUP% --name %BACKEND_APP_NAME%
echo.
pause
