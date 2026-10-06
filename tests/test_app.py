from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def reset_activity_state():
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
    activities["Soccer Club"]["participants"] = []


def test_get_activities_returns_activity_list():
    reset_activity_state()

    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Soccer Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant_for_activity():
    reset_activity_state()

    response = client.post("/activities/Soccer Club/signup?email=student@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up student@mergington.edu for Soccer Club"
    assert "student@mergington.edu" in activities["Soccer Club"]["participants"]


def test_signup_rejects_duplicate_participant():
    reset_activity_state()

    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant_from_activity():
    reset_activity_state()

    response = client.delete("/activities/Chess Club/participants/daniel@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered daniel@mergington.edu from Chess Club"
    assert "daniel@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404():
    reset_activity_state()

    response = client.delete("/activities/Chess Club/participants/ghost@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"


def test_signup_missing_activity_returns_404():
    reset_activity_state()

    response = client.post("/activities/Unknown Activity/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
