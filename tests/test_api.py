import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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


def create(client, **overrides):
    return client.post("/complaints", json={**VALID, **overrides})


def test_health_check(client):
    assert client.get("/api/health").status_code == 200


def test_dashboard_serves_frontend(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'id="complaint-form"' in response.text


def test_create_complaint(client):
    res = create(client)
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "pending"
    assert body["id"] == 1
    assert client.get("/complaints").json()[0]["title"] == VALID["title"]


def test_create_rejects_short_title(client):
    assert create(client, title="Bad").status_code == 422


def test_create_rejects_invalid_category(client):
    assert create(client, category="space").status_code == 422


def test_create_rejects_bad_phone(client):
    assert create(client, phone="abc").status_code == 422


def test_get_complaint_and_404(client):
    create(client)
    assert client.get("/complaints/1").status_code == 200
    assert client.get("/complaints/999").status_code == 404


def test_list_with_filters(client):
    create(client, category="road")
    create(client, category="water")
    assert len(client.get("/complaints").json()) == 2
    roads = client.get("/complaints", params={"category": "road"}).json()
    assert len(roads) == 1 and roads[0]["category"] == "road"


def test_pagination(client):
    for _ in range(3):
        create(client)
    assert len(client.get("/complaints", params={"limit": 2}).json()) == 2
    assert len(client.get("/complaints", params={"skip": 2}).json()) == 1


def test_update_status(client):
    create(client)
    res = client.patch(
        "/complaints/1/status", json={"status": "in_progress", "remarks": "Team sent"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"


def test_cannot_update_closed_complaint(client):
    create(client)
    client.patch("/complaints/1/status", json={"status": "resolved"})
    res = client.patch("/complaints/1/status", json={"status": "in_progress"})
    assert res.status_code == 400


def test_delete_complaint(client):
    create(client)
    assert client.delete("/complaints/1").status_code == 204
    assert client.get("/complaints/1").status_code == 404


def test_stats(client):
    create(client)
    create(client)
    client.patch("/complaints/1/status", json={"status": "resolved"})
    stats = client.get("/complaints/stats").json()
    assert stats["total"] == 2
    assert stats["pending"] == 1
    assert stats["resolved"] == 1
