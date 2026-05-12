import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activity database before each test."""
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield


def build_signup_url(activity_name: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/signup"


def test_get_activities_returns_activity_dictionary():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities
    assert "Chess Club" in response.json()


def test_signup_for_activity_adds_user():
    # Arrange
    client = TestClient(app)
    activity_name = "Art Club"
    email = "alexandra@mergington.edu"
    signup_url = build_signup_url(activity_name)
    initial_participants = list(activities[activity_name]["participants"])

    # Act
    response = client.post(signup_url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == len(initial_participants) + 1


def test_signup_for_existing_student_returns_400():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(build_signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_404():
    # Arrange
    client = TestClient(app)
    activity_name = "Cooking Club"
    email = "test@mergington.edu"

    # Act
    response = client.post(build_signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_removes_student():
    # Arrange
    client = TestClient(app)
    activity_name = "Basketball Team"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.delete(build_signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_student_returns_404():
    # Arrange
    client = TestClient(app)
    activity_name = "Gym Class"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(build_signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unregister_missing_activity_returns_404():
    # Arrange
    client = TestClient(app)
    activity_name = "Drama Club"
    email = "emma@mergington.edu"

    # Act
    response = client.delete(build_signup_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
