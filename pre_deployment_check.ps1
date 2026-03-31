# 🚀 Quick Deployment Script
# Run this before pushing to GitHub

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Pre-Deployment Check" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "C:\Users\Interfocus\Desktop\UNIMAR\telecontrol"

# Check 1: Make sure .env is ignored
Write-Host "✓ Checking .env protection..." -ForegroundColor Yellow
$envIgnored = git check-ignore .env
if ($envIgnored) {
    Write-Host "  ✅ .env is properly ignored" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  WARNING: .env might be committed!" -ForegroundColor Red
    Write-Host "  Run: git rm --cached .env" -ForegroundColor Yellow
}

Write-Host ""

# Check 2: Git status
Write-Host "✓ Checking repository status..." -ForegroundColor Yellow
git status --short
Write-Host ""

# Check 3: Test if Azure OpenAI works
Write-Host "✓ Testing Azure OpenAI connection..." -ForegroundColor Yellow
python test_azure_openai.py 2>&1 | Select-String -Pattern "SUCCESS|ERROR" | Select-Object -First 1
Write-Host ""

# Check 4: List what will be committed
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Files Ready to Commit" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
git status --short | Where-Object { $_ -match "^\s*[AM]" }
Write-Host ""

# Summary
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Ready to Deploy?" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. git add ." -ForegroundColor Cyan
Write-Host "  2. git commit -m 'feat: Add RAG system with Azure OpenAI'" -ForegroundColor Cyan
Write-Host "  3. git push origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deployment platforms:" -ForegroundColor White
Write-Host "  • Frontend: https://vercel.com (Next.js)" -ForegroundColor Cyan
Write-Host "  • Backend:  https://railway.app (FastAPI)" -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 Full guide: GITHUB_VERCEL_DEPLOYMENT.md" -ForegroundColor Green
Write-Host ""
