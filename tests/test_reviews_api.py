"""Tests for the review and rating API endpoints."""

import pytest
from flask import session


class TestCreateReviewAPI:
    """Tests for POST /api/reviews."""

    def test_create_review_api(self, app, client):
        """Test that a logged-in user can create a review via the API."""
        from auth import register_user

        with app.app_context():
            register_user("reviewcreator", "reviewcr@test.com", "password123")

        with client:
            # Login
            client.post("/login", data={
                "username": "reviewcreator",
                "password": "password123",
            })

            # Create a review
            response = client.post("/api/reviews", json={
                "igdb_id": 111222,
                "rating": 4,
                "body": "Great game, really enjoyed it!",
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data is not None
            assert data["rating"] == 4
            assert data["body"] == "Great game, really enjoyed it!"
            assert "id" in data
            assert "created_at" in data

    def test_create_review_api_duplicate(self, app, client):
        """Test that duplicate reviews return 409."""
        from auth import register_user

        with app.app_context():
            register_user("dupcreator", "dupcr@test.com", "password123")

        with client:
            client.post("/login", data={
                "username": "dupcreator",
                "password": "password123",
            })

            # First review should succeed
            client.post("/api/reviews", json={
                "igdb_id": 333444,
                "rating": 5,
                "body": "First review",
            })

            # Duplicate should fail
            response = client.post("/api/reviews", json={
                "igdb_id": 333444,
                "rating": 3,
                "body": "Second attempt",
            })
            assert response.status_code == 409
            data = response.get_json()
            assert data is not None
            assert "error" in data


class TestGetReviewsAPI:
    """Tests for GET /api/reviews/<igdb_id>."""

    def test_get_reviews_api(self, app, client):
        """Test that reviews are returned for a game with reviews."""
        from auth import register_user
        from models import Game, Review, db

        with app.app_context():
            user = register_user("reviewgetter", "reviewget@test.com", "password123")
            game = Game(igdb_id=555666, name="Test Game")
            db.session.add(game)
            db.session.commit()

            review = Review(user_id=user.id, game_id=game.id, rating=3, body="Decent game")
            db.session.add(review)
            db.session.commit()

        response = client.get("/api/reviews/555666")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["rating"] == 3
        assert data[0]["body"] == "Decent game"
        assert data[0]["username"] == "reviewgetter"

    def test_get_reviews_api_no_reviews(self, client):
        """Test that a game with no reviews returns an empty list."""
        response = client.get("/api/reviews/999999")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_reviews_api_multiple(self, app, client):
        """Test multiple reviews for the same game."""
        from auth import register_user
        from models import Game, Review, db

        with app.app_context():
            user1 = register_user("multiuser1", "multi1@test.com", "password123")
            user2 = register_user("multiuser2", "multi2@test.com", "password123")
            game = Game(igdb_id=777888, name="Multi Review Game")
            db.session.add(game)
            db.session.commit()

            db.session.add(Review(user_id=user1.id, game_id=game.id, rating=5, body="Great!"))
            db.session.add(Review(user_id=user2.id, game_id=game.id, rating=2, body="Not great"))
            db.session.commit()

        response = client.get("/api/reviews/777888")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2

        # Check that both usernames appear
        usernames = {r["username"] for r in data}
        assert "multiuser1" in usernames
        assert "multiuser2" in usernames


class TestReviewRatingValidation:
    """Tests for review rating validation."""

    def test_review_rating_validation_too_high(self, app, client):
        """Test that a rating > 5 returns 400."""
        from auth import register_user

        with app.app_context():
            register_user("ratingvalid", "ratingv@test.com", "password123")

        with client:
            client.post("/login", data={
                "username": "ratingvalid",
                "password": "password123",
            })

            response = client.post("/api/reviews", json={
                "igdb_id": 100200,
                "rating": 6,
                "body": "This should fail",
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data is not None
            assert "error" in data

    def test_review_rating_validation_too_low(self, app, client):
        """Test that a rating < 1 returns 400."""
        from auth import register_user

        with app.app_context():
            register_user("ratinglow", "ratinglow@test.com", "password123")

        with client:
            client.post("/login", data={
                "username": "ratinglow",
                "password": "password123",
            })

            response = client.post("/api/reviews", json={
                "igdb_id": 100201,
                "rating": 0,
                "body": "This should fail too",
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data is not None
            assert "error" in data

    def test_review_rating_validation_missing(self, app, client):
        """Test that missing rating returns 400."""
        from auth import register_user

        with app.app_context():
            register_user("ratingmissing", "ratingmiss@test.com", "password123")

        with client:
            client.post("/login", data={
                "username": "ratingmissing",
                "password": "password123",
            })

            response = client.post("/api/reviews", json={
                "igdb_id": 100202,
                "body": "No rating provided",
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data is not None
            assert "error" in data

    def test_review_rating_validation_non_integer(self, app, client):
        """Test that a non-integer rating returns 400."""
        from auth import register_user

        with app.app_context():
            register_user("ratingnonint", "ratingni@test.com", "password123")

        with client:
            client.post("/login", data={
                "username": "ratingnonint",
                "password": "password123",
            })

            response = client.post("/api/reviews", json={
                "igdb_id": 100203,
                "rating": "not-a-number",
                "body": "Invalid rating",
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data is not None
            assert "error" in data
