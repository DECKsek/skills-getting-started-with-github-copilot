"""Unit tests for the FastAPI backend using AAA (Arrange-Act-Assert) pattern"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_returns_all_activities(self, client):
        """
        Arrange: Client is ready
        Act: Call GET /activities
        Assert: Response contains all 9 activities with correct structure
        """
        # Arrange
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert "Basketball Team" in activities
        assert "Soccer Club" in activities
        assert "Art Club" in activities
        assert "Drama Club" in activities
        assert "Debate Club" in activities
        assert "Science Club" in activities
    
    def test_activity_has_correct_structure(self, client):
        """
        Arrange: Client is ready
        Act: Call GET /activities and get one activity
        Assert: Activity has all required fields
        """
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        
        # Assert
        assert set(chess_club.keys()) == expected_fields
        assert isinstance(chess_club["description"], str)
        assert isinstance(chess_club["schedule"], str)
        assert isinstance(chess_club["max_participants"], int)
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_student_can_signup_for_activity(self, client):
        """
        Arrange: Fresh client with empty participant lists
        Act: POST signup with student email to an activity
        Assert: Response confirms signup and student is added to participants
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "alice@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "message" in response.json()
        assert student_email in response.json()["message"]
        
        # Verify student was actually added
        activities_response = client.get("/activities")
        enrolled_students = activities_response.json()[activity_name]["participants"]
        assert student_email in enrolled_students
        assert len(enrolled_students) == 1
    
    def test_multiple_students_can_signup_for_same_activity(self, client):
        """
        Arrange: Fresh client
        Act: POST signup with two different student emails to same activity
        Assert: Both students are added to participants list
        """
        # Arrange
        activity_name = "Programming Class"
        student_email_1 = "bob@mergington.edu"
        student_email_2 = "carol@mergington.edu"
        
        # Act
        response_1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email_1}
        )
        response_2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email_2}
        )
        
        # Assert
        assert response_1.status_code == 200
        assert response_2.status_code == 200
        
        # Verify both students are enrolled
        activities_response = client.get("/activities")
        enrolled_students = activities_response.json()[activity_name]["participants"]
        assert student_email_1 in enrolled_students
        assert student_email_2 in enrolled_students
        assert len(enrolled_students) == 2
    
    def test_signup_is_independent_across_activities(self, client):
        """
        Arrange: Fresh client
        Act: Sign up same student to two different activities
        Assert: Student is enrolled in both, but activities are independent
        """
        # Arrange
        student_email = "dave@mergington.edu"
        activity_1 = "Art Club"
        activity_2 = "Drama Club"
        
        # Act
        response_1 = client.post(
            f"/activities/{activity_1}/signup",
            params={"email": student_email}
        )
        response_2 = client.post(
            f"/activities/{activity_2}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response_1.status_code == 200
        assert response_2.status_code == 200
        
        # Verify student is enrolled in both activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert student_email in activities[activity_1]["participants"]
        assert student_email in activities[activity_2]["participants"]
        
        # Verify each activity only has one participant (this student)
        assert len(activities[activity_1]["participants"]) == 1
        assert len(activities[activity_2]["participants"]) == 1


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_student_can_unregister_from_activity(self, client):
        """
        Arrange: Student signed up for an activity
        Act: POST unregister to remove the student
        Assert: Response confirms unregister and student is removed from participants
        """
        # Arrange
        activity_name = "Soccer Club"
        student_email = "eve@mergington.edu"
        
        # First, sign up the student
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Verify student is enrolled
        response_before = client.get("/activities")
        assert student_email in response_before.json()[activity_name]["participants"]
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "message" in response.json()
        assert student_email in response.json()["message"]
        
        # Verify student was actually removed
        activities_response = client.get("/activities")
        enrolled_students = activities_response.json()[activity_name]["participants"]
        assert student_email not in enrolled_students
        assert len(enrolled_students) == 0
    
    def test_unregister_preserves_other_students(self, client):
        """
        Arrange: Two students signed up for same activity
        Act: Unregister one student
        Assert: Other student remains enrolled
        """
        # Arrange
        activity_name = "Basketball Team"
        student_email_1 = "frank@mergington.edu"
        student_email_2 = "grace@mergington.edu"
        
        # Sign up both students
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email_1}
        )
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email_2}
        )
        
        # Act - unregister first student
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email_1}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify first student is removed but second remains
        activities_response = client.get("/activities")
        enrolled_students = activities_response.json()[activity_name]["participants"]
        assert student_email_1 not in enrolled_students
        assert student_email_2 in enrolled_students
        assert len(enrolled_students) == 1


class TestRootRedirect:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Client is ready
        Act: Call GET / with follow_redirects=False to capture redirect
        Assert: Response is a 307 redirect to /static/index.html
        """
        # Arrange
        # Note: TestClient follows redirects by default
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
