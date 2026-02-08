# Host CheckMate — Step by Step

You’ll do two things: **1) put the API online (Render)** and **2) put the website online (Vercel)**. Then they talk to each other.

You need:
- Your repo on GitHub (e.g. TheDankDork/CXC or CheckMate)
- A **Gemini API key** (from Google AI Studio)
- About 10 minutes

---

# Part 1: Host the backend (API) on Render

## Step 1.1 — Open Render and sign in

1. Go to **https://render.com** in your browser.
2. Click **Get Started** or **Sign In**.
3. Choose **Sign in with GitHub** and approve so Render can see your repos.

---

## Step 1.2 — Create a new Web Service

1. On the Render **Dashboard**, click the blue **New +** button.
2. Click **Web Service**.

---

## Step 1.3 — Connect your repo

1. Under **Connect a repository**, you’ll see a list of your GitHub repos.
2. Find **CXC** or **CheckMate** (whatever your repo is called) and click **Connect** next to it.
   - If you don’t see it, click **Configure account** and give Render access to that repo, then try again.

---

## Step 1.4 — Fill in the service settings

Use these **exactly** (unless you want a different name):

| Field | What to enter |
|-------|-------------------------------|
| **Name** | `checkmate-api` (or any name you like) |
| **Region** | Pick the one closest to you |
| **Branch** | `main` |
| **Root Directory** | Leave **empty** |
| **Runtime** | **Python 3** |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT app:app` |

Do **not** change **Instance Type** on the free tier.

---

## Step 1.5 — Add your secret (API key)

1. Scroll to the **Environment** section.
2. Click **Add Environment Variable**.
3. **Key:** `GEMINI_API_KEY`  
   **Value:** paste your Gemini API key (the long string from Google AI Studio).
4. Leave **FRONTEND_URL** for later (optional). You can add it after the frontend is deployed if you use a custom domain.

---

## Step 1.6 — Create the service and wait

1. Click the green **Create Web Service** at the bottom.
2. Render will build and deploy. Wait until the log shows **Your service is live** (often 2–5 minutes).
3. At the top of the page you’ll see a URL like:  
   **https://checkmate-api.onrender.com**  
4. **Copy that URL** and keep it — you’ll use it in Part 2.

If the build fails, check the build log. Most often it’s a typo in Build Command or Start Command; fix and use **Manual Deploy** to try again.

---

# Part 2: Host the frontend (website) on Vercel

## Step 2.1 — Open Vercel and sign in

1. Go to **https://vercel.com** in your browser.
2. Click **Sign Up** or **Log In**.
3. Choose **Continue with GitHub** and approve so Vercel can see your repos.

---

## Step 2.2 — Import your project

1. On the Vercel dashboard, click **Add New…** → **Project**.
2. You’ll see a list of GitHub repos. Find **CXC** (or **CheckMate**) and click **Import** next to it.

---

## Step 2.3 — Set the root directory (important)

1. After import, you’ll see **Configure Project**.
2. Find **Root Directory**. Click **Edit**.
3. Type: `frontend/checkmate`
4. Confirm so the root is **frontend/checkmate** (not the repo root). This is where the React app lives.

---

## Step 2.4 — Add the backend URL (so the site can call your API)

1. In the same **Configure Project** page, find **Environment Variables**.
2. **Name:** `VITE_API_BASE_URL`  
   **Value:** the URL you copied from Render, e.g. `https://checkmate-api.onrender.com`  
   - No slash at the end.
   - Use **Production** (and **Preview** if you want preview deploys to work too).
3. Click **Add** (or **Save**).

---

## Step 2.5 — Deploy

1. Click **Deploy** at the bottom.
2. Wait for the build to finish (usually 1–2 minutes).
3. When it’s done, you’ll see **Congratulations!** and a link like **https://your-project.vercel.app**.

---

## Step 2.6 — Open your hosted site

1. Click **Visit** (or the project URL).
2. That’s your live CheckMate site. Try entering a URL and clicking **Analyze**.
3. The first request might be slow (Render free tier wakes the backend up); after that it should be normal.

---

# Quick reference

| What | Where |
|------|--------|
| Backend (API) | Render → your Web Service URL, e.g. `https://checkmate-api.onrender.com` |
| Frontend (website) | Vercel → your Project URL, e.g. `https://your-project.vercel.app` |
| Backend env vars | Render → your service → **Environment** tab |
| Frontend env vars | Vercel → your project → **Settings** → **Environment Variables** |

---

# If something goes wrong

- **“Failed to fetch” on the live site**  
  - Check that the **backend** is running on Render (open its URL in the browser; you might see an error or “Method Not Allowed” for GET — that’s OK).  
  - Make sure **VITE_API_BASE_URL** on Vercel is exactly your Render URL (no trailing slash, https).

- **Backend build failed on Render**  
  - Check the build log.  
  - Confirm Build Command = `pip install -r requirements.txt` and Start Command = `gunicorn --bind 0.0.0.0:$PORT app:app`.

- **Frontend build failed on Vercel**  
  - Confirm **Root Directory** is `frontend/checkmate`.  
  - Check the build log for missing dependencies or errors.

- **First request is very slow**  
  - On the free tier, Render puts the backend to sleep after a while. The first request wakes it; later ones are faster.

That’s it. Once both are deployed, you’ve hosted the whole thing.
