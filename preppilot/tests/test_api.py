import os

# Use an isolated in-file SQLite DB and the mock AI for tests.
os.environ["DATABASE_URL"] = "sqlite:///./test_preppilot.db"
os.environ["GROQ_API_KEY"] = ""

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def register(client, email="a@example.com"):
    r = client.post("/api/auth/register", json={"email": email, "full_name": "Test", "password": "password123"})
    assert r.status_code == 201
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_register_duplicate_and_login(client):
    register(client)
    dup = client.post("/api/auth/register", json={"email": "A@example.com", "full_name": "T", "password": "password123"})
    assert dup.status_code == 409
    ok = client.post("/api/auth/login", json={"email": "a@example.com", "password": "password123"})
    assert ok.status_code == 200
    bad = client.post("/api/auth/login", json={"email": "a@example.com", "password": "wrongpass"})
    assert bad.status_code == 401


def test_requires_auth(client):
    assert client.get("/api/sessions").status_code == 401


def test_full_interview_flow(client):
    h = register(client)
    r = client.post("/api/sessions", json={"role": "Python Developer", "level": "junior", "num_questions": 3}, headers=h)
    assert r.status_code == 201
    session = r.json()
    assert len(session["questions"]) == 3

    qid = session["questions"][0]["id"]
    ans = client.post(
        f"/api/sessions/{session['id']}/questions/{qid}/answer",
        json={"answer": "I would use FastAPI with SQLAlchemy and write pytest tests for every endpoint."},
        headers=h,
    )
    assert ans.status_code == 200
    assert 1 <= ans.json()["score"] <= 10

    summary = client.get(f"/api/sessions/{session['id']}/summary", headers=h).json()
    assert summary["answered"] == 1 and summary["total"] == 3

    assert len(client.get("/api/sessions", headers=h).json()) == 1
    assert client.delete(f"/api/sessions/{session['id']}", headers=h).status_code == 204


def test_users_cannot_see_each_others_sessions(client):
    h1 = register(client, "one@example.com")
    h2 = register(client, "two@example.com")
    s = client.post("/api/sessions", json={"role": "Django Developer"}, headers=h1).json()
    assert client.get(f"/api/sessions/{s['id']}", headers=h2).status_code == 404
