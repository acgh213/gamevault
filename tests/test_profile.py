"""Tests for the enhanced profile page with stats and activity."""

import pytest
from flask import template_rendered
from contextlib import contextmanager


@contextmanager
def captured_templates(app):
    """Context manager to capture rendered templates during requests."""
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class TestProfilePageRenders:
    """Tests that the profile page renders correctly."""

    def test_profile_page_renders(self, app, client):
        """Test that the profile page returns 200 for an existing user."""
        from auth import register_user

        with app.app_context():
            register_user("proftest1", "prof1@test.com", "password123")

        response = client.get("/profile/proftest1")
        assert response.status_code == 200
        assert b"proftest1" in response.data

    def test_profile_page_uses_profile_template(self, app, client):
        """Test that the profile page renders profile.html."""
        from auth import register_user

        with app.app_context():
            register_user("proftest2", "prof2@test.com", "password123")

        with captured_templates(app) as templates:
            client.get("/profile/proftest2")
            assert len(templates) > 0
            template_name = templates[0][0].name
            assert template_name == "profile.html"


class TestProfileShowsStats:
    """Tests that profile stats are displayed correctly."""

    def test_profile_shows_total_reviews(self, app, client):
        """Test that the profile page shows total review count."""
        from auth import register_user
        from models import Game, Review, db

        with app.app_context():
            user = register_user("statstest1", "stats1@test.com", "password123")
            game = Game(igdb_id=10001, name="Test Game 1")
            db.session.add(game)
            db.session.commit()
            for i in range(3):
                review = Review(user_id=user.id, game_id=game.id, rating=4, body=f"Review {i}")
                db.session.add(review)
            db.session.commit()

        response = client.get("/profile/statstest1")
        assert response.status_code == 200
        assert b"3" in response.data  # total reviews

    def test_profile_shows_average_rating(self, app, client):
        """Test that the profile page shows average rating."""
        from auth import register_user
        from models import Game, Review, db

        with app.app_context():
            user = register_user("statstest2", "stats2@test.com", "password123")
            game = Game(igdb_id=10002, name="Test Game 2")
            db.session.add(game)
            db.session.commit()
            for rating in [4, 5]:
                review = Review(user_id=user.id, game_id=game.id, rating=rating)
                db.session.add(review)
            db.session.commit()

        response = client.get("/profile/statstest2")
        html = response.data.decode("utf-8")
        assert "4.5" in html  # avg of 4 and 5

    def test_profile_shows_game_count(self, app, client):
        """Test that the profile page shows count of unique games reviewed."""
        from auth import register_user
        from models import Game, Review, db

        with app.app_context():
            user = register_user("statstest3", "stats3@test.com", "password123")
            games = [
                Game(igdb_id=20001, name="Unique Game A"),
                Game(igdb_id=20002, name="Unique Game B"),
            ]
            for g in games:
                db.session.add(g)
            db.session.commit()
            for g in games:
                review = Review(user_id=user.id, game_id=g.id, rating=4)
                db.session.add(review)
            # Add a second review on one game — shouldn't increase game count
            extra = Review(user_id=user.id, game_id=games[0].id, rating=5)
            db.session.add(extra)
            db.session.commit()

        response = client.get("/profile/statstest3")
        html = response.data.decode("utf-8")
        # Should show 2 unique games, not 3 reviews
        assert "2" in html

    def test_profile_shows_zero_stats_for_no_reviews(self, app, client):
        """Test that a user with no reviews shows zeros appropriately."""
        from auth import register_user

        with app.app_context():
            register_user("zerotest", "zero@test.com", "password123")

        response = client.get("/profile/zerotest")
        html = response.data.decode("utf-8")
        assert "0" in html or b"No reviews" in response.data


class TestProfileShowsReviews:
    """Tests that the profile page displays user reviews."""

    def test_profile_shows_reviews_content(self, app, client):
        """Test that the profile page shows review content."""
        from auth import register_user
        from models import Game, Review, db

        with app.app_context():
            user = register_user("reviewtest1", "rev1@test.com", "password123")
            game = Game(igdb_id=30001, name="Game With Reviews")
            db.session.add(game)
            db.session.commit()
            review = Review(
                user_id=user.id,
                game_id=game.id,
                rating=5,
                body="This is a fantastic game!",
            )
            db.session.add(review)
            db.session.commit()

        response = client.get("/profile/reviewtest1")
        assert b"This is a fantastic game!" in response.data

    def test_profile_shows_game_name_in_reviews(self, app, client):
        """Test that the profile page shows the game name for each review."""
        from auth import register_user
        from models import Game, Review, db

        with app.app_context():
            user = register_user("reviewtest2", "rev2@test.com", "password123")
            game = Game(igdb_id=30002, name="Legendary Game Name")
            db.session.add(game)
            db.session.commit()
            review = Review(user_id=user.id, game_id=game.id, rating=4)
            db.session.add(review)
            db.session.commit()

        response = client.get("/profile/reviewtest2")
        assert b"Legendary Game Name" in response.data

    def test_profile_shows_cover_images(self, app, client):
        """Test that the profile page shows cover images for reviewed games."""
        from auth import register_user
        from models import Game, Review, db

        with app.app_context():
            user = register_user("reviewtest3", "rev3@test.com", "password123")
            game = Game(
                igdb_id=30003,
                name="Game With Cover",
                cover_url="https://example.com/cover.jpg",
            )
            db.session.add(game)
            db.session.commit()
            review = Review(user_id=user.id, game_id=game.id, rating=4)
            db.session.add(review)
            db.session.commit()

        response = client.get("/profile/reviewtest3")
        assert b"cover.jpg" in response.data or b"cover_url" in response.data

    def test_profile_shows_empty_state_for_no_reviews(self, app, client):
        """Test that the profile page shows empty state when no reviews."""
        from auth import register_user

        with app.app_context():
            register_user("norevuser", "norev@test.com", "password123")

        response = client.get("/profile/norevuser")
        html = response.data.decode("utf-8")
        assert "No reviews" in html
