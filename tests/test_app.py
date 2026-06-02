"""
Tests for the Mergington High School API using the AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test."""
    original = {
        name: {**data, "participants": list(data["participants"])}
        for name, data in activities.items()
    }
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


# --- GET /activities ---

def test_get_activities_returns_all_activities(client):
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_get_activities_includes_participants(client):
    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


# --- POST /activities/{activity_name}/signup ---

def test_signup_adds_student_to_activity(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_returns_confirmation_message(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert "message" in response.json()


def test_signup_for_nonexistent_activity_returns_404(client):
    # Arrange
    email = "student@mergington.edu"
    activity = "Nonexistent Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_signup_twice_returns_400(client):
    # Arrange
    email = "michael@mergington.edu"  # already in Chess Club
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


# --- DELETE /activities/{activity_name}/participants ---

def test_unregister_removes_student_from_activity(client):
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_returns_confirmation_message(client):
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert "message" in response.json()


def test_unregister_from_nonexistent_activity_returns_404(client):
    # Arrange
    email = "student@mergington.edu"
    activity = "Nonexistent Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_unregister_student_not_in_activity_returns_404(client):
    # Arrange
    email = "nothere@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
