# Pre-Deployment Checklist

**Complete this checklist BEFORE running DEPLOY_AZURE.bat**

## System Requirements ✓

- [ ] Windows 10/11 with 5GB+ free disk space
- [ ] 4GB+ available RAM
- [ ] Stable internet connection

## Software Prerequisites ✓

- [ ] Docker Desktop installed
  - Test: Run `docker --version` in Command Prompt
  - Expected: `Docker version 20.x.x` or higher
  
- [ ] Node.js 18+ installed
  - Test: Run `node --version` in Command Prompt
  - Expected: `v18.x.x` or higher
  
- [ ] NPM installed (comes with Node.js)
  - Test: Run `npm --version` in Command Prompt
  - Expected: `8.x.x` or higher
  
- [ ] Azure CLI installed
  - Test: Run `az --version` in Command Prompt
  - Expected: `azure-cli 2.5x.x` or higher
  
- [ ] Git installed
  - Test: Run `git --version` in Command Prompt
  - Expected: `git version 2.x.x` or higher

## Azure Account ✓

- [ ] Active Azure subscription
- [ ] Can access Azure Portal (portal.azure.com)
- [ ] Permissions to create resources
- [ ] Brazil South region is available for your account
  - Check: https://azure.microsoft.com/global-infrastructure/services/

## Project Files ✓

- [ ] Project located at: `C:\Users\Interfocus\Desktop\UNIMAR\telecontrol`
- [ ] Backend files present:
  - [ ] `api.py`
  - [ ] `ml.py`
  - [ ] `requirements.txt`
  - [ ] `Dockerfile`
  - [ ] `classificador_semantico.pkl`
  - [ ] `classificador_defeitos.pkl`
  - [ ] `classificador_defeitos_classes.pkl`
  
- [ ] Frontend files present:
  - [ ] `telecon-ai/package.json`
  - [ ] `telecon-ai/app/` (source files)
  - [ ] `telecon-ai/next.config.js`

## Credentials ✓

- [ ] Azure OpenAI Endpoint: `https://breakfixtesteunimar.cognitiveservices.azure.com/`
- [ ] Azure OpenAI API Key: `<SUA_CHAVE_AZURE_OPENAI>`
- [ ] Deployment Name: `gpt-4.1-mini-2`
- [ ] API Version: `2024-08-01-preview`

## Azure CLI Authentication ✓

- [ ] Run: `az login` (browser window opens)
- [ ] Sign in with your Azure account
- [ ] Verify: `az account show` returns your account info

## Configuration Files ✓

- [ ] `DEPLOY_AZURE.bat` exists in project root
- [ ] `MANUAL_DEPLOYMENT_GUIDE.md` exists (backup reference)
- [ ] `QUICK_REFERENCE.md` exists (troubleshooting reference)

## Pre-Deployment Validation ✓

### Test Docker Build (Optional but recommended)

```cmd
cd C:\Users\Interfocus\Desktop\UNIMAR\telecontrol
docker build -t test-build:latest .
```

- [ ] Build completes without errors
- [ ] Output shows: `Successfully tagged test-build:latest`

### Test Node Build (Optional but recommended)

```cmd
cd C:\Users\Interfocus\Desktop\UNIMAR\telecontrol\telecon-ai
npm install --dry-run
npm run build --dry-run
```

- [ ] No errors in output
- [ ] Both commands complete successfully

## Deployment Settings ✓

- [ ] Resource Group Name: `telecontrol-rg` ✓
- [ ] App Service Plan: `telecontrol-plan` ✓
- [ ] Backend App: `telecontrol-api` ✓
- [ ] Frontend App: `telecontrol-web` ✓
- [ ] Region: `brazilsouth` ✓
- [ ] SKU: `F1` (Free tier) ✓

## Understanding the Risks ✓

- [ ] Understand that first deployment may take 30-45 minutes
- [ ] Understand Free tier has 60 min/day CPU limit (for testing only)
- [ ] Understand you can upgrade to Basic (B1) tier for production
- [ ] Understand credentials should never be shared publicly
- [ ] Understand .env files should never be committed to git

## Commitment ✓

- [ ] I have completed all checks above
- [ ] I am ready to deploy
- [ ] I understand the process
- [ ] I have notes on my resource names and URLs

---

## Go/No-Go Decision

### ✅ GO (All checks passed)
If all items above are checked, you're ready to deploy!

```cmd
cd C:\Users\Interfocus\Desktop\UNIMAR\telecontrol
DEPLOY_AZURE.bat
```

### ⚠️ WAIT (Some items unchecked)
If any items are unchecked:

1. **Missing Software**: Install the missing tool
2. **Not Logged In**: Run `az login`
3. **Missing Files**: Check file locations
4. **Unsure**: Re-read the relevant section

---

## During Deployment

### Expected Behavior

✅ Script shows progress messages for each step
✅ Docker build takes 5-10 minutes (normal, don't interrupt)
✅ npm build takes 3-5 minutes (normal)
✅ Total time: 30-45 minutes (normal)

### What to Avoid

❌ Don't close Command Prompt
❌ Don't interrupt the script (Ctrl+C stops it)
❌ Don't use computer heavily (use other device if possible)
❌ Don't open multiple Command Prompts

### If Script Fails

If the script fails at any point:

1. **Note the error message** (screenshot or write it down)
2. **Check troubleshooting** in QUICK_REFERENCE.md
3. **Try again** - many failures are network-related
4. **Or go manual** - use MANUAL_DEPLOYMENT_GUIDE.md

---

## After Deployment Success

### Verify Immediately

1. **Check Azure Portal**
   - Go to https://portal.azure.com
   - Find resource group: `telecontrol-rg`
   - Verify both web apps are "Running"

2. **Test Health Endpoint** (wait 2-3 minutes first)
   - Open browser: `https://telecontrol-api.azurewebsites.net/health`
   - Expected: JSON with `"status": "ok"`

3. **Test Frontend**
   - Open browser: `https://telecontrol-web.azurewebsites.net`
   - Should load the TeleControl UI

4. **Test Prediction**
   - Enter: "celular não liga tela preta"
   - Click: "Analisar"
   - Should return classification

### Document Your URLs

Save these for future reference:
```
Frontend: https://telecontrol-web.azurewebsites.net
Backend:  https://telecontrol-api.azurewebsites.net
Health:   https://telecontrol-api.azurewebsites.net/health
API Docs: https://telecontrol-api.azurewebsites.net/docs
```

### Next Steps

- [ ] Monitor logs for 24 hours
- [ ] Test with real data
- [ ] Upgrade to Basic (B1) if moving to production
- [ ] Set up monitoring and alerts
- [ ] Configure custom domain (optional)

---

## Confidence Level

If you have checked all items above:

**Confidence**: 95%+ that deployment will succeed ✅

**Time to Success**: 30-45 minutes ⏱️

**Next Action**: Run `DEPLOY_AZURE.bat` 🚀

---

## Support Resources

If you get stuck:

1. **Check QUICK_REFERENCE.md** - Common commands and fixes
2. **Check MANUAL_DEPLOYMENT_GUIDE.md** - Step-by-step details
3. **Check Azure Docs**: https://docs.microsoft.com/azure/app-service/
4. **Check Logs**: `az webapp log tail -g telecontrol-rg -n telecontrol-api`

---

**Last Updated**: March 27, 2026  
**Status**: ✅ Ready for Deployment  
**Action**: Run DEPLOY_AZURE.bat when ready

