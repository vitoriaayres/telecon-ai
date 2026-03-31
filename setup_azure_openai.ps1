# Azure OpenAI Integration - Quick Start Script
# Run this script to set up everything automatically

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Azure OpenAI Integration Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location "C:\Users\Interfocus\Desktop\UNIMAR\telecontrol"

# Step 1: Install dependencies
Write-Host "📦 Step 1: Installing dependencies..." -ForegroundColor Yellow
Write-Host ""
pip install -r requirements.txt
Write-Host ""

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Error installing dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Check if .env exists
Write-Host "📝 Step 2: Checking .env configuration..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".env") {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
    
    # Check if Azure variables are set
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "AZURE_OPENAI_ENDPOINT" -and $envContent -notmatch "YOUR-RESOURCE-NAME") {
        Write-Host "✅ Azure OpenAI seems configured" -ForegroundColor Green
        $configured = $true
    } else {
        Write-Host "⚠️  .env exists but Azure OpenAI not configured" -ForegroundColor Yellow
        $configured = $false
    }
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "📋 Creating .env from template..." -ForegroundColor Cyan
    Copy-Item ".env.azure_template" ".env"
    Write-Host "✅ .env created! Please edit it with your Azure credentials" -ForegroundColor Green
    $configured = $false
}

Write-Host ""

# Step 3: Instructions
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

if (-not $configured) {
    Write-Host "🔧 You need to configure Azure OpenAI:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Open Azure Portal: https://portal.azure.com" -ForegroundColor White
    Write-Host "2. Create Azure OpenAI resource (see AZURE_OPENAI_SETUP.md)" -ForegroundColor White
    Write-Host "3. Deploy gpt-4o-mini model" -ForegroundColor White
    Write-Host "4. Copy endpoint and API key" -ForegroundColor White
    Write-Host "5. Edit .env file and fill in:" -ForegroundColor White
    Write-Host "   - AZURE_OPENAI_ENDPOINT" -ForegroundColor Cyan
    Write-Host "   - AZURE_OPENAI_API_KEY" -ForegroundColor Cyan
    Write-Host "   - AZURE_OPENAI_DEPLOYMENT_NAME" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📖 Detailed guide: AZURE_OPENAI_SETUP.md" -ForegroundColor Green
    Write-Host ""
}

Write-Host "6. Test the connection:" -ForegroundColor White
Write-Host "   python test_azure_openai.py" -ForegroundColor Cyan
Write-Host ""

Write-Host "7. Test structured output:" -ForegroundColor White
Write-Host "   python classificador.py" -ForegroundColor Cyan
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  📚 Documentation" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "• Setup Guide:       AZURE_OPENAI_SETUP.md" -ForegroundColor White
Write-Host "• Implementation:    IMPLEMENTACAO_LLM_AZURE.md" -ForegroundColor White
Write-Host "• Configuration:     .env (edit this file)" -ForegroundColor White
Write-Host ""

Write-Host "✨ Ready to implement RAG (Step B) after LLM works!" -ForegroundColor Green
Write-Host ""
