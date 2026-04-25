import pytest
from datetime import datetime

class TestUserModel:
    def test_user_creation(self, db):
        from models import User

        user = User(username="testuser", email="test@example.com", password_hash="hashed_pw")
        db.session.add(user)
        db.session.commit()

        saved = db.session.get(User, user.id)
        assert saved is not None
        assert saved.username == "testuser"
        assert saved.email == "test@example.com"
        assert saved.password_hash == "hashed_pw"
        assert isinstance(saved.created_at, datetime)

    def test_user_unique_username(self, db):
        from models import User

        User(username="uniqueuser", email="a@example.com", password_hash="pw").save()
        with pytest.raises(Exception):
            User(username="uniqueuser", email="b@example.com", password_hash="pw").save()

    def test_user_unique_email(self, db):
        from models import User

        User(username="user1", email="dup@example.com", password_hash="pw").save()
        with pytest.raises(Exception):
            User(username="user2", email="dup@example.com", password_hash="pw").save()


class TestGameModel:
    def test_game_creation(self, db):
        from models import Game

        game = Game(
            igdb_id=12345,
            name="Test Game",
            release_date="2024-01-15",
            cover_url="https://example.com/cover.jpg",
            summary="A test game",
            genres=["Action", "RPG"],
            platforms=["PC", "PlayStation 5"],
        )
        db.session.add(game)
        db.session.commit()

        saved = db.session.get(Game, game.id)
        assert saved is not None
        assert saved.igdb_id == 12345
        assert saved.name == "Test Game"
        assert saved.release_date == "2024-01-15"
        assert saved.cover_url == "https://example.com/cover.jpg"
        assert saved.summary == "A test game"
        assert saved.genres == ["Action", "RPG"]
        assert saved.platforms == ["PC", "PlayStation 5"]
        assert isinstance(saved.created_at, datetime)

    def test_game_unique_igdb_id(self, db):
        from models import Game

        Game(igdb_id=999, name="Game A").save()
        with pytest.raises(Exception):
            Game(igdb_id=999, name="Game B").save()


class TestReviewModel:
    def test_review_creation(self, db):
        from models import User, Game, Review

        user = User(username="reviewer", email="reviewer@example.com", password_hash="pw").save()
        game = Game(igdb_id=111, name="Reviewed Game").save()

        review = Review(user_id=user.id, game_id=game.id, rating=4, body="Great game!")
        db.session.add(review)
        db.session.commit()

        saved = db.session.get(Review, review.id)
        assert saved is not None
        assert saved.user_id == user.id
        assert saved.game_id == game.id
        assert saved.rating == 4
        assert saved.body == "Great game!"
        assert isinstance(saved.created_at, datetime)
        assert isinstance(saved.updated_at, datetime)

    def test_review_rating_range(self, db):
        from models import Review

        with pytest.raises(Exception):
            Review(rating=6, body="Out of range")

    def test_review_min_rating(self, db):
        from models import Review

        with pytest.raises(Exception):
            Review(rating=0, body="Below range")


class TestGameListModel:
    def test_game_list_creation(self, db):
        from models import User, Game, GameList

        user = User(username="listmaker", email="list@example.com", password_hash="pw").save()
        game1 = Game(igdb_id=1, name="Game One").save()
        game2 = Game(igdb_id=2, name="Game Two").save()

        game_list = GameList(
            user_id=user.id,
            name="My Favorites",
            description="My favorite games",
            is_public=True,
        )
        game_list.games.append(game1)
        game_list.games.append(game2)
        db.session.add(game_list)
        db.session.commit()

        saved = db.session.get(GameList, game_list.id)
        assert saved is not None
        assert saved.user_id == user.id
        assert saved.name == "My Favorites"
        assert saved.description == "My favorite games"
        assert saved.is_public is True
        assert isinstance(saved.created_at, datetime)
        assert len(saved.games) == 2
        assert saved.games[0].name == "Game One"
        assert saved.games[1].name == "Game Two"
