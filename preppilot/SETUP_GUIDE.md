# PrepPilot - Setup, Run and GitHub Push Guide

Follow the steps in order. Commands are given for **Windows (PowerShell)** and **macOS/Linux**.

---

## Part 1: Setup

### 1. Install the tools

| Tool | Version | Check with |
|------|---------|------------|
| Python | 3.10 or newer | `python --version` |
| Git | any recent | `git --version` |
| MySQL Server | 8.x (optional, see step 5) | `mysql --version` |
| VS Code | any | - |

Downloads: python.org, git-scm.com, dev.mysql.com/downloads.
On Windows, tick **"Add Python to PATH"** during install.

### 2. Open the project

Unzip `preppilot.zip`, then in a terminal:

```bash
cd preppilot
code .          # optional: opens VS Code
```

### 3. Create a virtual environment

Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```
If PowerShell blocks the script, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your prompt.

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Choose a database

**Option A: SQLite (fastest, zero setup).** Good for a first run.
In `.env` use: `DATABASE_URL=sqlite:///./preppilot.db`

**Option B: MySQL (matches your resume).**
Log in to MySQL and create the database:

```sql
CREATE DATABASE preppilot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

In `.env` use (replace `your_password`):
`DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/preppilot`

Tables are created automatically when the app starts.

### 6. Configure environment variables

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

Edit `.env`:

- `DATABASE_URL`: from step 5.
- `SECRET_KEY`: any long random string. Generate one with:
  `python -c "import secrets; print(secrets.token_hex(32))"`
- `GROQ_API_KEY`: get a free key at https://console.groq.com (API Keys > Create). **Leave empty to use the built-in mock AI**, which is fine for testing.

Never commit `.env`. It is already in `.gitignore`.

---

## Part 2: Run

### 1. Start the server

```bash
uvicorn app.main:app --reload
```

### 2. Open the app

- App: http://127.0.0.1:8000
- API docs (Swagger): http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/api/health

### 3. Try it

1. Click **Register**, create an account.
2. Enter a role (for example "Python Developer"), pick a level, click **Start**.
3. Type an answer under a question and click **Submit answer** to get a score and feedback.

### 4. Run the tests

```bash
pytest -q
```
You should see `5 passed`.

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` not found | Use `python3`, or reinstall Python with PATH enabled |
| `Access denied for user 'root'` | Wrong MySQL password in `DATABASE_URL` |
| `Unknown database 'preppilot'` | Run the `CREATE DATABASE` command in step 5 |
| `cryptography` error with MySQL 8 | It is already in requirements; run `pip install -r requirements.txt` again |
| `502 AI service error` | Check `GROQ_API_KEY`, or leave it empty to use the mock AI |
| Port 8000 busy | `uvicorn app.main:app --reload --port 8001` |

---

## Part 3: Push to GitHub

Your GitHub username: **sagarpoojary01**.

### 1. Configure Git (first time only)

```bash
git config --global user.name "Sagar"
git config --global user.email "sagarpoojary144@gmail.com"
```

### 2. Check that secrets are not tracked

```bash
git init
git status
```
`.env`, `venv/` and `*.db` must **not** appear in the list. If `.env` appears, stop and check `.gitignore`.

### 3. Make the first commit

```bash
git add .
git commit -m "Initial commit: PrepPilot AI mock interview coach"
git branch -M main
```

### 4. Create the repository on GitHub

1. Go to https://github.com/new
2. Repository name: `preppilot`
3. Description: `AI mock interview coach built with FastAPI, MySQL and Llama 3.1 via Groq`
4. Choose **Public** (recruiters can see it)
5. Do **not** tick "Add a README" or ".gitignore" (you already have them)
6. Click **Create repository**

### 5. Connect and push

```bash
git remote add origin https://github.com/sagarpoojary01/preppilot.git
git push -u origin main
```

GitHub no longer accepts your account password on the command line. When asked to log in, either:

- sign in through the browser window that Git Credential Manager opens (easiest), or
- create a **Personal Access Token**: GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic) > Generate new token, tick `repo`, and paste the token as the password.

### 6. Check it worked

Open https://github.com/sagarpoojary01/preppilot. You should see all files and the README.

### 7. Pushing later changes

```bash
git add .
git commit -m "Describe what you changed"
git push
```

### 8. Make the repo look good for recruiters

- Add topics: `fastapi`, `python`, `mysql`, `llama`, `groq`, `jwt`
- Pin the repo on your GitHub profile
- Add a screenshot of the app to the README
- Add the project to your resume:
  **PrepPilot | AI Mock Interview Coach** - Python, FastAPI, MySQL, Groq API, Llama 3.1 8B, JWT, pytest

### If a push is rejected

- `remote origin already exists`: run `git remote set-url origin https://github.com/sagarpoojary01/preppilot.git`
- `failed to push some refs`: you probably ticked "Add a README" on GitHub. Run `git pull origin main --allow-unrelated-histories`, then `git push`.
