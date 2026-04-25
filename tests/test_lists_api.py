"""Tests for list/shelf API endpoints."""

import pytest
from flask import session


class TestListsAPI:
    """Tests for the list API endpoints."""

    def test_list_requires_auth(self, client):
        """Test that creating a list without login returns 302."""
        response = client.post(
            "/api/lists",
            json={"name": "My List"},
            follow_redirects=False,
        )
        assert response.status_code == 302

    def test_create_list(self, app, client):
        """Test that a logged-in user can create a list."""
        from auth import register_user

        with app.app_context():
            register_user("listcreator", "list@test.com", "password123")

        with client:
            client.post("/login", data={
                "username": "listcreator",
                "password": "password123",
            })

            response = client.post("/api/lists", json={
                "name": "My Favorites",
                "description": "My favorite games",
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["name"] == "My Favorites"
            assert data["description"] == "My favorite games"

    def test_add_game_to_list(self, app, client):
        """Test that a logged-in user can add a game to a list."""
        from auth import register_user
        from models import Game, GameList, db

        with app.app_context():
            user = register_user("listadder", "add@test.com", "password123")
            game = Game(igdb_id=99991, name="Test Game").save()
            game_list = GameList(user_id=user.id, name="My List").save()
            list_id = game_list.id
            game_id = game.id

        with client:
            client.post("/login", data={
                "username": "listadder",
                "password": "password123",
            })

            response = client.post(
                f"/api/lists/{list_id}/games",
                json={"game_id": game_id},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert "added" in data["message"].lower()

            # Verify the relationship persisted
            with app.app_context():
                gl = db.session.get(GameList, list_id)
                assert gl is not None
                assert any(g.id == game_id for g in gl.games)

    def test_remove_game_from_list(self, app, client):
        """Test that a logged-in user can remove a game from a list."""
        from auth import register_user
        from models import Game, GameList, db

        with app.app_context():
            user = register_user("listremover", "remove@test.com", "password123")
            game = Game(igdb_id=99992, name="Remove Game").save()
            game_list = GameList(user_id=user.id, name="My List")
            game_list.games.append(game)
            game_list.save()
            list_id = game_list.id
            game_id = game.id

        with client:
            client.post("/login", data={
                "username": "listremover",
                "password": "password123",
            })

            response = client.delete(
                f"/api/lists/{list_id}/games/{game_id}",
            )
            assert response.status_code == 200
            data = response.get_json()
            assert "removed" in data["message"].lower()

            # Verify the relationship was removed
            with app.app_context():
                gl = db.session.get(GameList, list_id)
                assert gl is not None
                assert not any(g.id == game_id for g in gl.games)
