# Quick Railway Deployment Script
# Run this to automate some verification steps

# SETUP: Save as deploy_railway.sh (Mac/Linux) or deploy_railway.ps1 (Windows)

echo "🚂 Railway Deployment Quick Check"
echo "=================================="
echo ""

# Check 1: Python version
echo "✓ Checking Python version..."
python --version
if [ $? -ne 0 ]; then
  echo "❌ Python not found. Install from python.org"
  exit 1
fi
echo ""

# Check 2: Git status
echo "✓ Checking Git status..."
git status
echo ""
echo "⚠️  Make sure:"
echo "   - No .env file in changes"
echo "   - Model files (.pkl) are added"
echo "   - Type 'q' to exit git status if needed"
echo ""

# Check 3: .env in gitignore
echo "✓ Checking .gitignore..."
if grep -q "^\.env$" .gitignore; then
  echo "✅ .env is in .gitignore"
else
  echo "❌ .env NOT in .gitignore!"
  echo "   Add to .gitignore:"
  echo "   .env"
  exit 1
fi
echo ""

# Check 4: Model files exist
echo "✓ Checking model files..."
if [ -f "classificador_defeitos.pkl" ] && [ -f "classificador_defeitos_classes.pkl" ]; then
  echo "✅ Model files found"
else
  echo "❌ Model files missing!"
  echo "   Run: python trainamento_modelo.py"
  exit 1
fi
echo ""

# Check 5: requirements.txt exists
echo "✓ Checking requirements.txt..."
if [ -f "requirements.txt" ]; then
  echo "✅ requirements.txt found"
  echo "   Dependencies:"
  head -5 requirements.txt
else
  echo "❌ requirements.txt missing!"
  exit 1
fi
echo ""

# Check 6: Dockerfile exists
echo "✓ Checking Dockerfile..."
if [ -f "Dockerfile" ]; then
  echo "✅ Dockerfile found"
else
  echo "❌ Dockerfile missing!"
  exit 1
fi
echo ""

# Check 7: API can import
echo "✓ Checking API imports..."
python -c "import api; print('✅ API imports successfully')" 2>&1 | grep -q "✅"
if [ $? -eq 0 ]; then
  echo "✅ All imports OK"
else
  echo "❌ API import failed!"
  echo "   Run: pip install -r requirements.txt"
  exit 1
fi
echo ""

# Check 8: Push to GitHub
echo "✓ Ready to push?"
echo "   Commands:"
echo "   git add ."
echo "   git commit -m 'chore: prepare for Railway deployment'"
echo "   git push origin main"
echo ""

echo "=================================="
echo "✅ All checks passed!"
echo ""
echo "Next steps:"
echo "1. Get Azure keys (AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY)"
echo "2. Push to GitHub (git push origin main)"
echo "3. Go to https://railway.app"
echo "4. New Project → Deploy from GitHub → Select telecontrol"
echo "5. Settings → Variables → Add 4 Azure vars"
echo "6. Deploy!"
echo ""
echo "For detailed guide, read: RAILWAY_CHECKLIST.md"
