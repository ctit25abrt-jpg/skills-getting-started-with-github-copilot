import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture()
def client():
    original_activities = copy.deepcopy(activities)
    with TestClient(app) as test_client:
        yield test_client
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_seeded_data(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity in payload
    assert payload[expected_activity]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Volleyball"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 400
    assert payload == {"detail": "Student is already signed up for this activity"}


def test_unregister_from_activity_removes_participant(client):
    # Arrange
    activity_name = "Gym Class"
    email = "john@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_activity_rejects_missing_participant(client):
    # Arrange
    activity_name = "Volleyball"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload == {"detail": "Student is not signed up for this activity"}