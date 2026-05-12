"""Pytest configuration and fixtures for backend tests"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def fresh_app():
    """
    Fixture providing a fresh app instance with reset in-memory data for test isolation.
    Each test gets its own copy of the activities data, preventing cross-test pollution.
    """
    # Clear existing participants to create a known state
    for activity in activities.values():
        activity["participants"] = []
    
    yield app
    
    # Cleanup after test
    for activity in activities.values():
        activity["participants"] = []


@pytest.fixture
def client(fresh_app):
    """
    Fixture providing a TestClient instance for making HTTP requests to the app.
    Uses the fresh_app fixture to ensure isolated state for each test.
    """
    return TestClient(fresh_app)
