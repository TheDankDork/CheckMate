# Hosting CheckMate

Deploy the **backend** (Flask API) and **frontend** (React) separately, then connect them.

---

## 1. Deploy backend (Render)

1. Go to [render.com](https://render.com) and sign in (e.g. with GitHub).
2. **New → Web Service**.
3. Connect the repo (e.g. `TheDankDork/CXC` or `TheDankDork/CheckMate`).
4. Use these settings:
   - **Name:** `checkmate-api` (or any name)
   - **Root Directory:** leave empty (repo root)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`
5. **Environment:**
   - `GEMINI_API_KEY` = your Gemini API key (secret)
   - `FRONTEND_URL` = your frontend URL (e.g. `https://your-app.vercel.app`) — optional; `*.vercel.app` is already allowed for CORS
6. Click **Create Web Service**. Wait for the first deploy.
7. Copy the service URL, e.g. `https://checkmate-api.onrender.com`. You’ll use it as the frontend API URL.

---

## 2. Deploy frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) and sign in (e.g. with GitHub).
2. **Add New → Project** and import the same repo.
3. Configure:
   - **Root Directory:** set to `frontend/checkmate` (click **Edit**, then enter `frontend/checkmate`).
   - **Framework Preset:** Vite (should be detected).
   - **Environment variable:**
     - Name: `VITE_API_BASE_URL`
     - Value: your Render backend URL, e.g. `https://checkmate-api.onrender.com`
     - Apply to Production (and Preview if you want).
4. Click **Deploy**. Wait for the build.
5. Your app will be at a URL like `https://your-project.vercel.app`.

---

## 3. Connect frontend to backend

- The frontend is built with `VITE_API_BASE_URL`, so it will call your Render API.
- The backend allows CORS from `*.vercel.app` by default. If you use a custom domain, set `FRONTEND_URL` on Render to that URL (e.g. `https://checkmate.example.com`).

---

## Optional: one-repo deploy with Render Blueprint

If the repo has a `render.yaml` (Blueprint), you can use **New → Blueprint** in Render, connect the repo, and it will create the web service. Then set `GEMINI_API_KEY` and optionally `FRONTEND_URL` in the service’s Environment tab.

---

## Notes

- **Render free tier:** the backend may spin down after inactivity; the first request after a while can be slow.
- **Secrets:** never commit `.env`. Use each platform’s environment variables for API keys and URLs.
