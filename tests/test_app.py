import pytest
from fastapi.testclient import TestClient

from app.main import app, tasks


@pytest.fixture(autouse=True)
def reset_tasks():
    tasks.clear()
    yield
    tasks.clear()


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_task():
    response = client.post(
        "/tasks",
        json={"title": "Learn Jenkins"},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Learn Jenkins"
    assert response.json()["id"] == 1


def test_list_tasks():
    client.post("/tasks", json={"title": "Build Docker image"})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_task_not_found():
    response = client.get("/tasks/999")

    assert response.status_code == 404