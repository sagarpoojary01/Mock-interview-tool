# PrepPilot - AI Mock Interview Coach

PrepPilot generates role-specific interview questions with **Llama 3.1 8B (via the Groq API)**, scores your answers from 1 to 10, and gives short, actionable feedback. Progress is stored per user so you can track improvement over time.

Built with **FastAPI, SQLAlchemy, MySQL, JWT auth and a vanilla JavaScript frontend**.

## Features

- Register and log in (PBKDF2 password hashing, JWT bearer tokens)
- Start an interview for any role and level (intern, junior, mid, senior)
- AI-generated questions and AI-scored answers with feedback
- Session history with answered count and average score
- Users can only see their own sessions
- Built-in mock AI so the app runs without an API key
- Automated tests with pytest

## Tech stack

| Layer | Technology |
|-------|------------|
| API | FastAPI, Pydantic v2 |
| Database | MySQL (SQLite for quick start/tests), SQLAlchemy 2.0 |
| Auth | PyJWT, PBKDF2-HMAC-SHA256 |
| AI | Groq API, Llama 3.1 8B Instant |
| Frontend | HTML, CSS, JavaScript |
| Tests | pytest, FastAPI TestClient |

## Project structure

```
preppilot/
  app/
    main.py          FastAPI app, static files
    config.py        Environment settings
    database.py      Engine and session
    models.py        User, InterviewSession, Question
    schemas.py       Request/response models
    security.py      Password hashing, JWT, auth dependency
    llm.py           Groq client + mock fallback
    routers/
      auth.py        /api/auth/register, /api/auth/login
      interviews.py  /api/sessions ...
  static/            index.html, app.js, style.css
  tests/test_api.py
  requirements.txt
  .env.example
```

## Quick start

See **SETUP_GUIDE.md** for the full step-by-step guide. Short version:

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 (app) or http://127.0.0.1:8000/docs (interactive API docs).

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Create account, returns token |
| POST | /api/auth/login | Log in, returns token |
| POST | /api/sessions | Start an interview (AI generates questions) |
| GET | /api/sessions | List your sessions with scores |
| GET | /api/sessions/{id} | Session with all questions |
| GET | /api/sessions/{id}/summary | Answered count and average score |
| POST | /api/sessions/{id}/questions/{qid}/answer | Submit an answer, get score + feedback |
| DELETE | /api/sessions/{id} | Delete a session |

## Run tests

```bash
pytest -q
```

## Future improvements

- Voice answers with speech-to-text
- Per-skill score charts
- Docker Compose for app + MySQL
- Rate limiting on AI endpoints
