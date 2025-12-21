"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestActivities:
    """Test activity endpoints"""

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_has_required_fields(self, client):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity


class TestSignup:
    """Test signup endpoints"""

    def test_signup_for_activity(self, client):
        """Test signing up for an activity"""
        email = "test@example.com"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]

    def test_signup_already_registered(self, client):
        """Test signing up when already registered"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a nonexistent activity"""
        email = "test@example.com"
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": email}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant"""
        email = "newtester@example.com"
        # Sign up
        client.post("/activities/Tennis Club/signup", params={"email": email})
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Tennis Club"]["participants"]


class TestUnregister:
    """Test unregister endpoints"""

    def test_unregister_from_activity(self, client):
        """Test unregistering from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_not_registered(self, client):
        """Test unregistering when not registered"""
        email = "notregistered@example.com"
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a nonexistent activity"""
        email = "test@example.com"
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": email}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        email = "john@mergington.edu"  # Already in Gym Class
        # Unregister
        client.post("/activities/Gym Class/unregister", params={"email": email})
        # Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Gym Class"]["participants"]


class TestRoot:
    """Test root endpoint"""

    def test_root_redirect(self, client):
        """Test that root redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
