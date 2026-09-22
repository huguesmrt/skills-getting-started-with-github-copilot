from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    isolated_activities = deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", isolated_activities)

    with TestClient(app_module.app) as test_client:
        yield test_client, isolated_activities


def test_root_redirects_to_static_index(client):
    test_client, _ = client

    response = test_client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    test_client, isolated_activities = client

    response = test_client.get("/activities")

    assert response.status_code == 200
    assert response.json() == isolated_activities


def test_signup_adds_student_to_activity(client):
    test_client, _ = client
    email = "new.student@mergington.edu"

    response = test_client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    activities = test_client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_student(client):
    test_client, isolated_activities = client
    email = "michael@mergington.edu"

    response = test_client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert isolated_activities["Chess Club"]["participants"].count(email) == 1


def test_signup_rejects_unknown_activity(client):
    test_client, _ = client

    response = test_client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_requires_email(client):
    test_client, _ = client

    response = test_client.post("/activities/Chess%20Club/signup")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]


def test_unregister_removes_student_from_activity(client):
    test_client, _ = client
    email = "michael@mergington.edu"

    response = test_client.delete(
        "/activities/Chess%20Club/unregister", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    activities = test_client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_rejects_student_not_in_activity(client):
    test_client, isolated_activities = client
    original_participants = isolated_activities["Chess Club"]["participants"].copy()

    response = test_client.delete(
        "/activities/Chess%20Club/unregister",
        params={"email": "not.enrolled@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert isolated_activities["Chess Club"]["participants"] == original_participants


def test_unregister_rejects_unknown_activity(client):
    test_client, _ = client

    response = test_client.delete(
        "/activities/Unknown%20Club/unregister",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_requires_email(client):
    test_client, _ = client

    response = test_client.delete("/activities/Chess%20Club/unregister")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]