# Deploy CheckMate yourself (quick steps)

I can’t sign into Render or Vercel from here, so you need to log in once, then you can deploy with a few commands.

---

## 1. Backend on Render (one-time in the browser)

1. Open **https://render.com** → sign in with GitHub.
2. **New → Web Service** → connect repo **TheDankDork/CXC** (or CheckMate).
3. Settings:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn --bind 0.0.0.0:$PORT app:app`
4. **Environment** → Add:
   - `GEMINI_API_KEY` = your Gemini API key
5. **Create Web Service** → wait for deploy.
6. Copy the URL, e.g. `https://checkmate-api.onrender.com`.

---

## 2. Frontend on Vercel (CLI – you run it)

In a terminal:

```powershell
cd c:\Users\ThinkPad\Documents\GitHub\CXC\frontend\checkmate
npx vercel login
```

Log in in the browser when prompted, then:

```powershell
$env:VITE_API_BASE_URL = "https://checkmate-api.onrender.com"   # use YOUR Render URL from step 1
npx vercel deploy --prod -e "VITE_API_BASE_URL=$env:VITE_API_BASE_URL"
```

Or run the script (after `vercel login`):

```powershell
cd c:\Users\ThinkPad\Documents\GitHub\CXC\frontend\checkmate
$env:VITE_API_BASE_URL = "https://checkmate-api.onrender.com"
.\deploy-vercel.ps1
```

Vercel will print your live URL (e.g. `https://checkmate-xxx.vercel.app`).

---

## 3. Optional: allow your frontend URL in the backend

In **Render → your service → Environment**, add:

- `FRONTEND_URL` = your Vercel URL (e.g. `https://checkmate-xxx.vercel.app`)

Then redeploy the backend. (CORS already allows `*.vercel.app`, so this is only needed for a custom domain.)

---

**Summary:** You do step 1 (Render) in the browser once; step 2 (Vercel) is two commands after `vercel login`.
