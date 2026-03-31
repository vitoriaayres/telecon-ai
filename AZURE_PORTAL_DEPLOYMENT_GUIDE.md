# 🌐 Azure Portal Manual Deployment Guide

**For TeleControl Application - No Azure CLI Required**

**Status**: Visual step-by-step guide  
**Difficulty**: Easy (click buttons, follow screenshots)  
**Time**: ~45-60 minutes  
**Best For**: When Azure CLI has authentication issues  

---

## 📋 Overview

This guide deploys your TeleControl application entirely through the **Azure Portal web interface**. No command line needed!

### What You'll Do

1. **Create Resource Group** (container for all resources)
2. **Create App Service Plan** (compute allocation)
3. **Deploy Backend** (FastAPI + ML models in Docker)
4. **Deploy Frontend** (Next.js React app)
5. **Configure CORS and URLs**
6. **Test the deployment**

---

## 🚀 Part 1: Create Resource Group

### Step 1.1: Open Azure Portal

1. Go to: https://portal.azure.com
2. Sign in with your student account
3. Wait for the dashboard to load

### Step 1.2: Create New Resource Group

1. Click the **blue "Create a resource"** button (top left)
2. Search for: `resource group`
3. Click on **Resource Group**
4. Click **Create**

### Step 1.3: Fill Resource Group Details

Fill in these values:

```
Subscription:      Azure for Students
Resource Group:    telecontrol-rg
Region:           Brazil South
```

Then click **Review + create** → **Create**

**Wait for deployment to complete** (~1-2 minutes)

---

## 🏗️ Part 2: Create App Service Plan

### Step 2.1: Navigate to Resource Group

1. In the search bar (top), search: `telecontrol-rg`
2. Click on the resource group when it appears

### Step 2.2: Create App Service Plan

1. Inside the resource group, click **Create**
2. Search for: `app service plan`
3. Click **App Service Plan**
4. Click **Create**

### Step 2.3: Fill App Service Plan Details

```
Subscription:           Azure for Students
Resource Group:         telecontrol-rg
Name:                  telecontrol-plan
Operating System:       Linux
Region:                Brazil South
Pricing tier:          Free F1
```

Then click **Review + create** → **Create**

**Wait for deployment** (~2-3 minutes)

---

## 🐳 Part 3: Deploy Backend (FastAPI + Docker)

### Step 3.1: Create Backend App Service

1. In the search bar, search: `app service`
2. Click **App Service**
3. Click **Create**

### Step 3.2: Fill Backend Details

```
Subscription:           Azure for Students
Resource Group:         telecontrol-rg
Name:                  telecontrol-api
Publish:               Docker Container (select this!)
Operating System:       Linux
Region:                Brazil South
App Service Plan:      telecontrol-plan
```

Click **Next: Docker >**

### Step 3.3: Docker Configuration

```
Image Source:           Docker Hub
Image and Tag:          python:3.11-slim
(We'll upload manually after creation)
```

Click **Review + create** → **Create**

**Wait for deployment** (~5 minutes)

### Step 3.4: Deploy Your Backend Code

Once the app service is created:

1. Search for: `telecontrol-api` in the search bar
2. Open the **telecontrol-api** app service
3. On the left sidebar, click: **Deployment Center**
4. Change settings:
   ```
   Source:          GitHub (or Local Git)
   ```

**Alternative - Upload via Zip:**

1. Go to **Development Tools** → **SSH**
2. Use SFTP to upload your project files
3. Or use **GitHub Actions** for continuous deployment

**For now, let's do the simpler approach:**

1. Go to **Configuration** (left sidebar)
2. Add these **App Settings**:

```
AZURE_OPENAI_ENDPOINT    = https://breakfixtesteunimar.cognitiveservices.azure.com/
AZURE_OPENAI_KEY         = [your API key]
AZURE_OPENAI_MODEL       = gpt-4.1-mini-2
AZURE_API_VERSION        = 2024-08-01-preview
CORS_ORIGINS             = https://telecontrol-web.azurewebsites.net
```

3. Click **Save**
4. Go back to **Overview**
5. Click **Restart** (top menu)

---

## 🎨 Part 4: Deploy Frontend (Next.js)

### Step 4.1: Create Frontend App Service

1. Click **Create a resource** (top)
2. Search: `app service`
3. Click **App Service** → **Create**

### Step 4.2: Fill Frontend Details

```
Subscription:           Azure for Students
Resource Group:         telecontrol-rg
Name:                  telecontrol-web
Publish:               Code (NOT Docker)
Runtime:               Node 18 LTS
Operating System:       Linux
Region:                Brazil South
App Service Plan:      telecontrol-plan
```

Click **Review + create** → **Create**

**Wait for deployment** (~5 minutes)

### Step 4.3: Deploy Frontend Code

Once the app service is created:

1. Search for: `telecontrol-web`
2. Open the **telecontrol-web** app service
3. Go to: **Deployment Center** (left sidebar)
4. Choose one:

**Option A: GitHub**
- Connect your GitHub repo
- Enable automatic deployment

**Option B: Local Git**
- Follow instructions to set up local git
- Push your `telecon-ai` folder

**Option C: Upload via Zip (Simplest)**
1. Go to: **Advanced Tools** → **Go** (Kudu)
2. Drag and drop your `telecon-ai` folder
3. Or use the file manager to upload

### Step 4.4: Configure Frontend Build

1. Go back to main app service
2. Click: **Configuration** (left sidebar)
3. Add **App Settings**:

```
NEXT_PUBLIC_API_URL       = https://telecontrol-api.azurewebsites.net
NODE_ENV                  = production
YARN_PRODUCTION           = true
```

4. Click **Save**

---

## 🔗 Part 5: Configure CORS

### Step 5.1: Backend CORS Configuration

1. Search for: `telecontrol-api`
2. Go to: **Configuration** → **App Settings**
3. Update:

```
CORS_ORIGINS = https://telecontrol-web.azurewebsites.net
```

4. Click **Save**
5. **Restart** the app service

---

## ✅ Part 6: Test Your Deployment

### Step 6.1: Get Your Public URLs

1. Search for: `telecontrol-api`
2. Click on it
3. Copy the URL from the top (it says "https://telecontrol-api.azurewebsites.net")

Repeat for `telecontrol-web` - copy its URL

### Step 6.2: Test Backend Health

1. Open a new browser tab
2. Go to: `https://telecontrol-api.azurewebsites.net/health`
3. You should see:
```json
{"status": "ok"}
```

If you see a blank page or error:
- Wait 2-3 minutes (app is starting)
- Check **Log Stream** in the app service for errors
- Restart the app service

### Step 6.3: Test Frontend

1. Open a new browser tab
2. Go to: `https://telecontrol-web.azurewebsites.net`
3. You should see the TeleControl UI
4. If you see a blank page:
   - Wait 2-3 minutes
   - Check **Log Stream** for errors

### Step 6.4: Test Full Flow

1. In frontend, enter a defect description:
   ```
   "celular não liga tela preta"
   ```
2. Click **Analisar**
3. Should return a classification from the backend ML model

---

## 🐛 Troubleshooting

### Problem: Backend returns 500 error

**Solution:**
1. Go to **telecontrol-api** app service
2. Click: **Log Stream** (left sidebar)
3. Check for error messages
4. Most common: Missing environment variables
5. Go to **Configuration** and verify all settings are there
6. **Restart** the app service

### Problem: Frontend shows blank page

**Solution:**
1. Open DevTools (F12)
2. Check **Console** tab for errors
3. Common issue: Wrong backend URL
4. Go to **Configuration** and fix `NEXT_PUBLIC_API_URL`
5. **Restart** the app service

### Problem: CORS error in frontend console

**Solution:**
1. Backend CORS_ORIGINS might be wrong
2. Go to **telecontrol-api** → **Configuration**
3. Set: `CORS_ORIGINS = https://telecontrol-web.azurewebsites.net`
4. **Restart** backend

### Problem: "App Service is loading"

**Solution:**
- Just wait 2-3 minutes
- Apps take time to start on Free tier
- Check **Log Stream** to see startup progress

---

## 📊 Cost Verification

After deployment:

1. Go to: **Cost Management + Billing** (left sidebar)
2. Click: **Costs by resource**
3. You should see:
   - telecontrol-api: $0 (Free tier)
   - telecontrol-web: $0 (Free tier)
   - Azure OpenAI: $5-10/month (usage-based)

**Total: ~$5-10/month for testing**

---

## 🎉 Success Indicators

Your deployment is successful when:

✅ Backend health check returns 200 OK  
✅ Frontend loads in browser  
✅ ML prediction works (returns classification)  
✅ No CORS errors in browser console  
✅ Both apps visible in Azure Portal as "Running"  

---

## 📱 After Deployment: Next Steps

### Immediate (24 hours)
- [ ] Monitor **Log Stream** for errors
- [ ] Test with various inputs
- [ ] Check response times

### Short Term (1 week)
- [ ] Set up **Application Insights** for monitoring
- [ ] Configure **Auto-scale** rules
- [ ] Set up email alerts

### Medium Term (if going production)
- [ ] Upgrade to **Basic (B1)** tier (~$13/month each)
- [ ] Set up **custom domain** (optional)
- [ ] Configure **continuous deployment** from GitHub

---

## 📞 Quick Reference

| Task | Where |
|------|-------|
| View logs | App Service → Log Stream |
| Change settings | App Service → Configuration |
| Restart app | App Service → Overview → Restart |
| Check costs | Billing → Costs by resource |
| Monitor performance | App Service → Metrics |
| Set up alerts | App Service → Alerts |

---

## ✨ Common Portal Navigation

**From Azure Portal Home:**

1. **Find an app service:**
   - Top search bar → type "telecontrol-api" → click it

2. **View all resources:**
   - Left sidebar → Resource groups → telecontrol-rg

3. **Check deployment status:**
   - Resource group → Click resource → Check top banner

4. **See error logs:**
   - App Service → Development Tools → Log Stream

---

## 🚨 Important Notes

- **Free tier limitation**: 60 minutes CPU per day (will pause after that)
- **Startup time**: First request takes 30-45 seconds (cold start)
- **Model loading**: Backend may take 2-3 minutes to load ML models on first boot
- **HTTPS**: All URLs are HTTPS (automatic with Azure)

---

## 📝 Saving Your URLs

After successful deployment, save these URLs:

```
Frontend:  https://telecontrol-web.azurewebsites.net
Backend:   https://telecontrol-api.azurewebsites.net
Health:    https://telecontrol-api.azurewebsites.net/health
Docs:      https://telecontrol-api.azurewebsites.net/docs
```

---

## 🎯 Final Checklist

- [ ] Created resource group (telecontrol-rg)
- [ ] Created App Service Plan (telecontrol-plan)
- [ ] Created backend app service (telecontrol-api)
- [ ] Configured backend environment variables
- [ ] Deployed backend code
- [ ] Created frontend app service (telecontrol-web)
- [ ] Configured frontend environment variables
- [ ] Deployed frontend code
- [ ] Tested backend health endpoint
- [ ] Tested frontend loads
- [ ] Tested full ML prediction flow
- [ ] No CORS errors in console
- [ ] Both apps running in portal

---

## 🆘 Need Help?

If you get stuck on any step:

1. **Take a screenshot** of the exact screen/error
2. **Note the step number** you're on
3. **Describe what you see** vs. what you expected

Common mistakes:
- Wrong resource group selected
- Typo in app name
- Environment variables not saved
- Not clicking "Save" after configuration
- Not restarting app after changes

---

## 📚 Azure Documentation

- **App Service Overview**: https://learn.microsoft.com/azure/app-service/
- **Docker in App Service**: https://learn.microsoft.com/azure/app-service/quickstart-docker-python
- **Next.js on Azure**: https://learn.microsoft.com/azure/app-service/quickstart-nodejs

---

**Ready? Start with Part 1: Create Resource Group!** 🚀

Let me know if you get stuck on any step and I can help guide you through it.

