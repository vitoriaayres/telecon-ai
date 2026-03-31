@echo off
echo Deleting all markdown files...

cd /d C:\Users\Interfocus\Desktop\UNIMAR\telecontrol

del /F /Q "QUICK_REFERENCE_AZURE.md"
del /F /Q "PROJECT_STATUS.md"
del /F /Q "IMPLEMENTACAO_LLM_AZURE.md"
del /F /Q "IDEIAS_MELHORIAS.md"
del /F /Q "GUIA_IMPLANTAR_GPT_AZURE.md"
del /F /Q "GUIA_AZURE_ML.md"
del /F /Q "GITHUB_VERCEL_DEPLOYMENT.md"
del /F /Q "FIXING_ISSUES.md"
del /F /Q "DEPLOYMENT_STATUS_CURRENT.md"
del /F /Q "AZURE_OPENAI_SETUP.md"
del /F /Q "ARQUITETURA.md"
del /F /Q "README.md"
del /F /Q "RAILWAY_SUMMARY.md"
del /F /Q "RAILWAY_DEPLOYMENT.md"
del /F /Q "RAILWAY_CHECKLIST.md"
del /F /Q "RAG_IMPLEMENTATION_GUIDE.md"
del /F /Q "QUICK_TEST.md"
del /F /Q "START_HERE_NOW.md"
del /F /Q "RESUMO_IMPLEMENTACAO.md"
del /F /Q "README_RAILWAY.md"
del /F /Q "START_HERE_RAILWAY.md"
del /F /Q "SUMMARY_OF_FIXES.md"

cd telecon-ai
del /F /Q "VERCEL_DEPLOY_SIMPLE.md"
del /F /Q "README.md"
del /F /Q "FRONTEND_BACKEND_EXPLAINED.md"
del /F /Q "DEPLOY_AZURE_GUIDE.md"
del /F /Q "CHECKLIST_DEPLOY.md"
del /F /Q "ARCHITECTURE_EXPLAINED.md"
del /F /Q "AGENTS.md"

cd ..
echo.
echo ✅ All markdown files deleted!
echo.
pause
