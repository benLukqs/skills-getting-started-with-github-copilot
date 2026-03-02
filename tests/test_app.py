"""
Unit tests for the FastAPI Mergington High School Activities API

Tests cover all endpoints with both happy path and error case scenarios:
- GET /activities
- GET / (redirect)
- POST /activities/{activity_name}/signup
- POST /activities/{activity_name}/unregister
"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Test that root route redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_dict(self, client):
        """Test that /activities returns a dictionary of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_get_activities_contains_all_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            
            # Validate field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_participants_are_strings(self, client):
        """Test that participants array contains string emails"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_data in activities.values():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation

    def test_get_activities_includes_chess_club(self, client):
        """Test that Chess Club activity is present"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "Chess Club" in activities
        assert activities["Chess Club"]["max_participants"] == 12


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful_for_new_participant(self, client):
        """Test successful signup of a new participant"""
        activity_name = "Chess Club"
        email = "new_student@mergington.edu"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_updates_participant_count(self, client):
        """Test that signup actually adds the participant to the activity"""
        activity_name = "Chess Club"
        email = "new_student@mergington.edu"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Get updated count
        response = client.get("/activities")
        updated_count = len(response.json()[activity_name]["participants"])
        
        assert updated_count == initial_count + 1
        assert email in response.json()[activity_name]["participants"]

    def test_signup_with_invalid_activity_returns_404(self, client):
        """Test that signup with non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email_returns_400(self, client):
        """Test that duplicate signup for same activity returns 400 error"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_same_email_different_activities_succeeds(self, client):
        """Test that same email can signup for different activities"""
        email = "test_student@mergington.edu"
        
        # Signup for Chess Club
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Signup for Programming Class
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups worked
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]

    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with email containing special characters"""
        activity_name = "Chess Club"
        email = "test+special@mergington.edu"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful_removes_participant(self, client):
        """Test successful unregister of an existing participant"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Unregister
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
        
        # Verify participant was removed
        response = client.get("/activities")
        updated_count = len(response.json()[activity_name]["participants"])
        assert updated_count == initial_count - 1
        assert email not in response.json()[activity_name]["participants"]

    def test_unregister_with_invalid_activity_returns_404(self, client):
        """Test that unregister with non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_nonexistent_participant_returns_404(self, client):
        """Test that unregister of non-existent participant returns 404"""
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_then_signin_again_succeeds(self, client):
        """Test that unregistering and re-registering works correctly"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Unregister
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify unregistered
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]
        
        # Re-register
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify re-registered
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]


class TestIntegrationSignupAndUnregister:
    """Integration tests for signup and unregister workflows"""

    def test_complete_signup_unregister_workflow(self, client):
        """Test complete workflow: signup -> verify -> unregister -> verify"""
        activity_name = "Tennis Club"
        email = "integration_test@mergington.edu"
        
        # 1. Verify email not in activity
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]
        
        # 2. Signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # 3. Verify email is now in activity
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]
        
        # 4. Unregister
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # 5. Verify email is no longer in activity
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]

    def test_multiple_signups_and_unregisters(self, client):
        """Test multiple participants signing up and unregistering"""
        activity_name = "Robotics Club"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu",
        ]
        
        # Signup all students
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are signed up
        response = client.get("/activities")
        activity_data = response.json()[activity_name]
        for email in emails:
            assert email in activity_data["participants"]
        
        # Unregister all except one
        for email in emails[:-1]:
            response = client.post(
                f"/activities/{activity_name}/unregister",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify only one remains
        response = client.get("/activities")
        activity_data = response.json()[activity_name]
        assert emails[-1] in activity_data["participants"]
        assert emails[0] not in activity_data["participants"]
        assert emails[1] not in activity_data["participants"]
