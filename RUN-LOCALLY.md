# Run CheckMate locally

**You need:** Python 3.10+, Node.js 18+, and a [Gemini API key](https://aistudio.google.com/apikey).

---

## 1. Clone and go to the project

```bash
git clone https://github.com/TheDankDork/CheckMate.git
cd CheckMate
```

(If the repo is still named CXC, use `CXC` instead of `CheckMate` in the URL and folder name.)

---

## 2. Backend (first terminal)

```bash
pip install -r requirements.txt
copy .env.example .env   # Windows. Mac/Linux: cp .env.example .env
```

Open `.env` and set your key: `GEMINI_API_KEY=your_key_here`

Then start the backend:

```bash
python app.py
```

Keep this running. You should see: `Running on http://127.0.0.1:5000`

---

## 3. Frontend (second terminal)

Open a **new** terminal. From the project folder:

```bash
cd frontend/checkmate
npm install
npm run dev
```

Keep this running. You should see: `Local: http://localhost:5173/`

---

## 4. Open the site

In your browser go to: **http://localhost:5173**

Enter a URL and click **Analyze**.

---

## If something breaks

- **"Failed to fetch"** → Start the backend (step 2).
- **Analysis fails / "Missing GEMINI_API_KEY"** → Create `.env`, add your key, restart the backend.
- **Port in use** → Stop whatever is using port 5000 or 5173, or use another port (e.g. `PORT=5001 python app.py`).
