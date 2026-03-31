# 🖥️ Local Development Setup Guide

**Run TeleControl on Your Computer (No Cloud Yet!)**

**Difficulty**: Easy  
**Time**: ~15-20 minutes  
**Best For**: Testing before cloud deployment  

---

## 📋 What You'll Do

1. **Start the Backend** (FastAPI on port 8000)
2. **Start the Frontend** (Next.js on port 3000)
3. **Test everything locally**
4. **Once working, THEN deploy to Azure/Railway**

---

## ✅ Prerequisites (Verify You Have These)

Open Command Prompt and run each:

```cmd
python --version
```
Should show: `Python 3.x.x` ✓

```cmd
node --version
```
Should show: `v18.x.x` or higher ✓

```cmd
npm --version
```
Should show: `8.x.x` or higher ✓

**If any are missing**, download and install:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/ (includes npm)

---

## 🚀 Part 1: Start the Backend (FastAPI)

### Step 1.1: Open Command Prompt #1

Press: `Windows + R` → type `cmd` → press Enter

### Step 1.2: Navigate to Project

```cmd
cd C:\Users\Interfocus\Desktop\UNIMAR\telecontrol
```

### Step 1.3: Install Backend Dependencies

```cmd
pip install -r requirements.txt
```

**Wait for it to complete** (~2-3 minutes)

You should see: `Successfully installed ...` at the end

### Step 1.4: Start Backend Server

```cmd
python api.py
```

**You should see:**
```
Uvicorn running on http://127.0.0.1:8000
```

**Leave this Command Prompt window OPEN!** (Don't close it)

✅ **Backend is now running on:** `http://localhost:8000`

---

## 🎨 Part 2: Start the Frontend (Next.js)

### Step 2.1: Open Command Prompt #2 (NEW WINDOW)

Press: `Windows + R` → type `cmd` → press Enter

(You should now have TWO Command Prompts open)

### Step 2.2: Navigate to Frontend Project

```cmd
cd C:\Users\Interfocus\Desktop\UNIMAR\telecontrol\telecon-ai
```

### Step 2.3: Install Frontend Dependencies

```cmd
npm install
```

**Wait for it to complete** (~3-5 minutes)

You should see: `added X packages` at the end

### Step 2.4: Start Frontend Development Server

```cmd
npm run dev
```

**You should see:**
```
> ready - started server on 0.0.0.0:3000
```

**Leave this Command Prompt window OPEN!** (Don't close it)

✅ **Frontend is now running on:** `http://localhost:3000`

---

## 🧪 Part 3: Test Everything

### Step 3.1: Open Your Browser

Open: **http://localhost:3000**

You should see:
- ✅ TeleControl UI loads
- ✅ Input field for defect description
- ✅ "Analisar" button visible

### Step 3.2: Test Backend Health

Open a new tab: **http://localhost:8000/health**

You should see:
```json
{"status": "ok"}
```

### Step 3.3: Test Full ML Prediction

1. Go back to: http://localhost:3000
2. Type in the input field:
   ```
   celular não liga tela preta
   ```
3. Click **"Analisar"**
4. Wait 2-3 seconds

You should see:
- ✅ Loading animation while processing
- ✅ Classification result returned
- ✅ No error messages

### Step 3.4: Test Backend API Directly

Open: **http://localhost:8000/docs**

You should see:
- ✅ Swagger UI (interactive API documentation)
- ✅ All endpoints listed
- ✅ Try them out!

---

## 📊 Check Both Terminals

### Backend Terminal (Command Prompt #1)
Should show activity like:
```
INFO:     127.0.0.1:xxxxx - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:xxxxx - "POST /predict HTTP/1.1" 200 OK
```

### Frontend Terminal (Command Prompt #2)
Should show:
```
> ready - started server on 0.0.0.0:3000
```

Both should be running smoothly.

---

## 🧪 Full Testing Checklist

- [ ] Frontend loads at http://localhost:3000
- [ ] Backend health check passes
- [ ] Can enter text in frontend
- [ ] ML prediction returns result
- [ ] No errors in browser console (F12)
- [ ] No errors in Command Prompt windows
- [ ] API Docs work at http://localhost:8000/docs

---

## 🛠️ Troubleshooting

### Problem: "Port 8000 already in use"

**Solution:**
```cmd
netstat -ano | findstr :8000
```
Then kill the process or use a different port:
```cmd
python api.py --port 8001
```

### Problem: "Port 3000 already in use"

**Solution:**
```cmd
netstat -ano | findstr :3000
```
Or use a different port:
```cmd
npm run dev -- -p 3001
```

### Problem: "Module not found" error

**Solution:**
- Go back and run `pip install -r requirements.txt` OR `npm install`
- Make sure you're in the correct directory

### Problem: ML prediction returns error

**Solution:**
1. Check that model files exist:
   - `classificador_semantico.pkl` (~80MB)
   - `classificador_defeitos.pkl` (~5MB)
   - `classificador_defeitos_classes.pkl` (<1MB)
2. Check backend terminal for error messages
3. Restart backend with: Ctrl+C (in backend terminal) then `python api.py` again

### Problem: Frontend shows "Cannot connect to backend"

**Solution:**
1. Make sure backend is running (check Command Prompt #1)
2. Backend should show: `Uvicorn running on http://127.0.0.1:8000`
3. Try refreshing frontend (Ctrl+R)
4. Check browser console (F12) for CORS errors

### Problem: Browser console shows CORS error

**Solution:**
1. The api.py already has CORS configured
2. Try a full page reload (Ctrl+Shift+R)
3. Check that both services are actually running

---

## 💾 Stopping the Services

When you want to stop:

### Stop Backend
1. Go to Command Prompt #1
2. Press: `Ctrl + C`
3. Wait for it to stop

### Stop Frontend
1. Go to Command Prompt #2
2. Press: `Ctrl + C`
3. Wait for it to stop

Then you can close both Command Prompts.

---

## 🔄 Restarting Services

To restart again:

**Backend:**
```cmd
cd C:\Users\Interfocus\Desktop\UNIMAR\telecontrol
python api.py
```

**Frontend:**
```cmd
cd C:\Users\Interfocus\Desktop\UNIMAR\telecontrol\telecon-ai
npm run dev
```

---

## 📝 What's Happening

### Backend (api.py)
- **Port**: 8000
- **Technology**: Python FastAPI
- **What it does**:
  - Loads ML models into memory
  - Processes predictions
  - Calls Azure OpenAI API
  - Returns classifications

### Frontend (npm run dev)
- **Port**: 3000
- **Technology**: Next.js + React
- **What it does**:
  - Shows the UI
  - Takes user input
  - Calls backend API
  - Displays results

Both need to run together for full functionality.

---

## 🎯 Success Indicators

✅ Everything works locally when:
1. Backend health endpoint returns 200 OK
2. Frontend loads without errors
3. ML prediction returns a classification
4. No console errors in browser (F12)
5. No errors in Command Prompt windows

---

## 📚 Useful URLs (When Running Locally)

| Purpose | URL |
|---------|-----|
| Frontend UI | http://localhost:3000 |
| Backend Health | http://localhost:8000/health |
| API Docs | http://localhost:8000/docs |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## 🧠 How to Read the Terminals

### Backend Terminal Logs
```
INFO:     Started server process [1234]
INFO:     Waiting for application startup.
INFO:     127.0.0.1:54321 - "POST /predict HTTP/1.1" 200 OK
```

Meaning:
- `INFO` = Normal log
- `127.0.0.1` = Your computer
- `POST /predict` = API call being made
- `200 OK` = Success!

### Frontend Terminal Logs
```
> ready - started server on 0.0.0.0:3000
ready - compiled client and server successfully
```

Meaning:
- Server is running
- No compile errors
- Ready to accept requests

---

## 🔐 Azure OpenAI Integration

Even running locally, the ML model can use Azure OpenAI:

1. Make sure these environment variables are set:
   ```cmd
   set AZURE_OPENAI_ENDPOINT=https://breakfixtesteunimar.cognitiveservices.azure.com/
   set AZURE_OPENAI_KEY=your_api_key_here
   set AZURE_OPENAI_MODEL=gpt-4.1-mini-2
   ```

2. Then start backend:
   ```cmd
   python api.py
   ```

3. Backend will use Azure OpenAI for predictions

---

## 📋 Next Steps After Local Testing Works

Once you verify everything works locally:

1. ✅ Take screenshots of working UI
2. ✅ Note any issues found
3. ✅ Fix any bugs locally first
4. ✅ THEN deploy to cloud (Azure/Railway)

Cloud deployment will be much easier once you know what works locally!

---

## 🎉 Quick Start Summary

```cmd
# Terminal 1 - Backend
cd C:\Users\Interfocus\Desktop\UNIMAR\telecontrol
pip install -r requirements.txt
python api.py

# Terminal 2 - Frontend (in new Command Prompt)
cd C:\Users\Interfocus\Desktop\UNIMAR\telecontrol\telecon-ai
npm install
npm run dev

# Then open browser
http://localhost:3000
```

That's it! 🚀

---

## 🆘 Stuck?

If something doesn't work:

1. **Take a screenshot** of the error
2. **Note what step** you're on
3. **Copy-paste any error messages**

Common issues all have solutions - just need to see the exact error!

---

**Ready? Open Command Prompt and start with Part 1!** ✨

