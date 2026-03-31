# Quick Azure Backend Test Script
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "         Testing Azure Backend Connection" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$backendUrl = "http://4.228.41.39:8000"

# Test 1: Health Check
Write-Host "[1/3] Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$backendUrl/health" -Method Get -TimeoutSec 10
    Write-Host "✅ SUCCESS: Backend is responding!" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Depth 3)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAILED: Cannot connect to backend!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "  1. Azure Container is stopped - check Azure Portal" -ForegroundColor Gray
    Write-Host "  2. IP address changed - verify in Azure Portal" -ForegroundColor Gray
    Write-Host "  3. Firewall blocking port 8000" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Go to: https://portal.azure.com" -ForegroundColor Cyan
    Write-Host "Navigate to: Container Instances" -ForegroundColor Cyan
    Write-Host "Check: Your container status and IP" -ForegroundColor Cyan
    pause
    exit 1
}

Write-Host ""

# Test 2: Prediction Endpoint
Write-Host "[2/3] Testing Prediction Endpoint..." -ForegroundColor Yellow
$testData = @{
    texto_cliente = "celular não liga tela preta"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$backendUrl/predict" -Method Post -Body $testData -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ SUCCESS: Prediction endpoint working!" -ForegroundColor Green
    
    if ($response.resultados -and $response.resultados.Count -gt 0) {
        $top = $response.resultados[0]
        Write-Host "Top prediction: $($top.defeito_sugerido) ($($top.confianca_pct)%)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ FAILED: Prediction endpoint error!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Check API Documentation
Write-Host "[3/3] Checking API Documentation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$backendUrl/docs" -Method Get -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ SUCCESS: API docs available at $backendUrl/docs" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  WARNING: Could not access API docs" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "                   Test Complete!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. If all tests passed - your backend is working!" -ForegroundColor Gray
Write-Host "  2. Run verify.bat to test everything" -ForegroundColor Gray
Write-Host "  3. Test the frontend at https://telecontrol-ai.vercel.app" -ForegroundColor Gray
Write-Host ""
pause
