import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import auth
from app.database import Base, get_db
from app.main import app

# A fresh in-memory database for every test, so tests never affect each other.
engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    with TestingSession() as db:
        auth.ensure_admin(db)  # admin / admin123 (the lifespan hook is not run by TestClient)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


VALID = {
    "title": "Broken street light",
    "description": "The street light near the ward office has been off for a week.",
    "category": "electricity",
    "citizen_name": "Ram Shrestha",
    "phone": "9800000000",
}


def login(client, username, password):
    res = client.post("/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def register(client, username):
    res = client.post("/auth/register", json={"username": username, "password": "secret123"})
    assert res.status_code == 201, res.text
    return login(client, username, "secret123")


@pytest.fixture()
def admin(client):
    return login(client, "admin", "admin123")


@pytest.fixture()
def alice(client):
    return register(client, "alice")


@pytest.fixture()
def bob(client):
    return register(client, "bob")


def create(client, headers, **overrides):
    return client.post("/complaints", json={**VALID, **overrides}, headers=headers)


# ---------- basics ----------

def test_health_check(client):
    assert client.get("/api/health").status_code == 200


def test_dashboard_serves_frontend(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'id="complaint-form"' in response.text


# ---------- auth ----------

def test_register_always_creates_citizen(client):
    res = client.post(
        "/auth/register", json={"username": "eve", "password": "secret123", "role": "admin"}
    )
    assert res.status_code == 201
    assert res.json()["role"] == "citizen"


def test_register_duplicate_username(client, alice):
    res = client.post("/auth/register", json={"username": "alice", "password": "secret123"})
    assert res.status_code == 409


def test_login_wrong_password(client):
    res = client.post("/auth/login", json={"username": "admin", "password": "nope"})
    assert res.status_code == 401


def test_endpoints_require_login(client):
    assert client.get("/complaints").status_code == 401
    assert client.post("/complaints", json=VALID).status_code == 401
    assert client.get("/complaints", headers={"Authorization": "Bearer junk"}).status_code == 401


def test_logout_invalidates_token(client, alice):
    assert client.post("/auth/logout", headers=alice).status_code == 204
    assert client.get("/auth/me", headers=alice).status_code == 401


# ---------- complaints ----------

def test_create_complaint(client, alice):
    res = create(client, alice)
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "pending"
    assert body["id"] == 1
    assert client.get("/complaints", headers=alice).json()[0]["title"] == VALID["title"]


def test_create_rejects_short_title(client, alice):
    assert create(client, alice, title="Bad").status_code == 422


def test_create_rejects_invalid_category(client, alice):
    assert create(client, alice, category="space").status_code == 422


def test_create_rejects_bad_phone(client, alice):
    assert create(client, alice, phone="abc").status_code == 422


def test_list_with_filters(client, alice):
    create(client, alice, category="road")
    create(client, alice, category="water")
    assert len(client.get("/complaints", headers=alice).json()) == 2
    roads = client.get("/complaints", params={"category": "road"}, headers=alice).json()
    assert len(roads) == 1 and roads[0]["category"] == "road"


def test_pagination(client, alice):
    for _ in range(3):
        create(client, alice)
    assert len(client.get("/complaints", params={"limit": 2}, headers=alice).json()) == 2
    assert len(client.get("/complaints", params={"skip": 2}, headers=alice).json()) == 1


# ---------- admin sees all, citizens see own ----------

def test_admin_views_all_complaints(client, admin, alice, bob):
    create(client, alice)
    create(client, bob)
    assert len(client.get("/complaints", headers=admin).json()) == 2
    assert len(client.get("/complaints", headers=alice).json()) == 1
    assert len(client.get("/complaints", headers=bob).json()) == 1


def test_citizen_cannot_read_others_complaint(client, alice, bob):
    create(client, alice)
    assert client.get("/complaints/1", headers=alice).status_code == 200
    assert client.get("/complaints/1", headers=bob).status_code == 404


def test_admin_can_read_any_complaint(client, admin, alice):
    create(client, alice)
    assert client.get("/complaints/1", headers=admin).status_code == 200
    assert client.get("/complaints/999", headers=admin).status_code == 404


def test_stats_are_scoped(client, admin, alice, bob):
    create(client, alice)
    create(client, bob)
    assert client.get("/complaints/stats", headers=admin).json()["total"] == 2
    assert client.get("/complaints/stats", headers=alice).json()["total"] == 1


# ---------- only admin changes status ----------

def test_admin_updates_status(client, admin, alice):
    create(client, alice)
    res = client.patch(
        "/complaints/1/status", json={"status": "in_progress", "remarks": "Team sent"}, headers=admin
    )
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"
    assert client.get("/complaints/1", headers=alice).json()["remarks"] == "Team sent"


def test_citizen_cannot_update_status(client, alice):
    create(client, alice)  # even on their own complaint
    res = client.patch("/complaints/1/status", json={"status": "resolved"}, headers=alice)
    assert res.status_code == 403
    assert client.get("/complaints/1", headers=alice).json()["status"] == "pending"


def test_anonymous_cannot_update_status(client, alice):
    create(client, alice)
    assert client.patch("/complaints/1/status", json={"status": "resolved"}).status_code == 401


def test_cannot_update_closed_complaint(client, admin, alice):
    create(client, alice)
    client.patch("/complaints/1/status", json={"status": "resolved"}, headers=admin)
    res = client.patch("/complaints/1/status", json={"status": "in_progress"}, headers=admin)
    assert res.status_code == 400


def test_only_admin_can_delete(client, admin, alice):
    create(client, alice)
    assert client.delete("/complaints/1", headers=alice).status_code == 403
    assert client.delete("/complaints/1", headers=admin).status_code == 204
    assert client.get("/complaints/1", headers=admin).status_code == 404


def test_stats(client, admin, alice):
    create(client, alice)
    create(client, alice)
    client.patch("/complaints/1/status", json={"status": "resolved"}, headers=admin)
    stats = client.get("/complaints/stats", headers=admin).json()
    assert stats["total"] == 2
    assert stats["pending"] == 1
    assert stats["resolved"] == 1
