# Run CheckMate on your machine

Follow these steps to open the website locally (backend + frontend).

---

## 1. Clone the repo

```bash
git clone https://github.com/TheDankDork/CXC.git
cd CXC
```

(Or use the CheckMate repo URL if the repo was moved.)

---

## 2. Backend (Flask API)

**Requirements:** Python 3.10+ and pip.

```bash
# From the repo root (CXC)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

**Add your API key** (so the backend can call Gemini):

- Copy the example file:  
  `copy .env.example .env`  (Windows) or `cp .env.example .env`  (Mac/Linux)
- Open `.env` and set your Gemini key:  
  `GEMINI_API_KEY=your_actual_key_here`

**Start the backend:**

```bash
python app.py
```

Leave this terminal open. You should see something like:  
`Running on http://127.0.0.1:5000`

---

## 3. Frontend (React app)

**Requirements:** Node.js 18+ and npm.

Open a **second** terminal. From the repo root:

```bash
cd frontend/checkmate
npm install
npm run dev
```

Leave this running. You should see something like:  
`Local: http://localhost:5173/`

---

## 4. Open the website

In your browser go to: **http://localhost:5173**

- The frontend will talk to the backend via a proxy (`/api` → port 5000), so you don’t need to change any URL.
- Enter a URL and click **Analyze** to test.

---

## Troubleshooting

| Issue | What to do |
|--------|------------|
| “Failed to fetch” | Make sure the **backend** is running in the first terminal (`python app.py`). |
| “Missing GEMINI_API_KEY” | Create `.env` from `.env.example` and set `GEMINI_API_KEY`. |
| Port 5000 or 5173 in use | Stop the other app using that port, or change the port (e.g. `PORT=5001 python app.py` for the backend). |
| `pip` or `python` not found | Use `py -m venv venv` and `py app.py` on Windows, or install Python and ensure it’s on your PATH. |

---

**Summary:** Two terminals — (1) `python app.py`, (2) `cd frontend/checkmate && npm run dev` — then open **http://localhost:5173**.
