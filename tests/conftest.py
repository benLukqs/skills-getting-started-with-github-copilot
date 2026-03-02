"""
Pytest configuration and fixtures for FastAPI app tests
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for making requests to the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """
    Provide a fresh copy of the default activities.
    This allows tests to work with known test data without modifying the global state.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
    }


@pytest.fixture
def sample_emails():
    """Provide sample email addresses for testing"""
    return {
        "new_student": "new_student@mergington.edu",
        "another_student": "another_student@mergington.edu",
        "existing_participant": "michael@mergington.edu",  # Already in Chess Club
    }


@pytest.fixture
def sample_activities():
    """Provide sample activity names for testing"""
    return {
        "valid": "Chess Club",
        "invalid": "Nonexistent Activity",
    }


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Reset activities to default state before each test.
    This ensures tests don't interfere with each other.
    """
    default_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team training and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis instruction and tournaments",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts exploration",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["grace@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performance and script writing",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for competitions",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Prepare for and compete in debate competitions",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sophia@mergington.edu", "michael@mergington.edu"]
        }
    }
    
    # Clear and repopulate the global activities dict
    activities.clear()
    activities.update(default_activities)
    
    yield  # Test runs here
    
    # Cleanup (if needed)
