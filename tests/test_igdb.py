"""Tests for the IGDB API client."""
import pytest
import responses
from igdb import IGDBClient


class TestIGDBClient:
    """Test suite for IGDBClient."""

    def test_client_initialization(self):
        """Test that client stores credentials and doesn't crash on init."""
        client = IGDBClient("test_client_id", "test_client_secret")
        assert client.client_id == "test_client_id"
        assert client.client_secret == "test_client_secret"
        assert client._token is None
        assert client._token_expires_at is None

    @responses.activate
    def test_search_returns_list(self):
        """Test that search_games returns a list of parsed game dicts."""
        # Mock the token endpoint
        responses.post(
            "https://id.twitch.tv/oauth2/token",
            json={
                "access_token": "mock_access_token",
                "expires_in": 3600,
                "token_type": "bearer",
            },
            status=200,
        )

        # Mock the IGDB games search endpoint
        mock_games = [
            {
                "id": 1026,
                "name": "The Legend of Zelda: Breath of the Wild",
                "first_release_date": 1485907200,
                "cover": {"id": 12345, "url": "//images.igdb.com/igdb/image/upload/t_thumb/co1r0c.jpg"},
                "summary": "Forget everything you know about The Legend of Zelda games.",
                "genres": [{"id": 31, "name": "Action-Adventure"}],
                "platforms": [{"id": 6, "name": "Nintendo Switch"}],
            }
        ]
        responses.post(
            "https://api.igdb.com/v4/games",
            json=mock_games,
            status=200,
        )

        client = IGDBClient("test_client_id", "test_client_secret")
        results = client.search_games("zelda", limit=5)

        assert isinstance(results, list)
        assert len(results) == 1
        game = results[0]
        assert game["id"] == 1026
        assert game["name"] == "The Legend of Zelda: Breath of the Wild"
        assert game["first_release_date"] == 1485907200
        assert game["cover"]["url"] == "//images.igdb.com/igdb/image/upload/t_thumb/co1r0c.jpg"
        assert game["summary"] == "Forget everything you know about The Legend of Zelda games."
        assert game["genres"] == [{"id": 31, "name": "Action-Adventure"}]
        assert game["platforms"] == [{"id": 6, "name": "Nintendo Switch"}]

        # Verify token was requested
        token_req = responses.calls[0].request
        assert token_req.url == "https://id.twitch.tv/oauth2/token"

        # Verify game search was called with correct body
        search_req = responses.calls[1].request
        assert search_req.url == "https://api.igdb.com/v4/games"
        assert 'search "zelda"' in search_req.body
        assert "limit 5" in search_req.body

    @responses.activate
    def test_get_game_returns_dict(self):
        """Test that get_game returns a single parsed game dict."""
        # Mock the token endpoint
        responses.post(
            "https://id.twitch.tv/oauth2/token",
            json={
                "access_token": "mock_access_token",
                "expires_in": 3600,
                "token_type": "bearer",
            },
            status=200,
        )

        # Mock the IGDB games endpoint for a single game lookup
        mock_games = [
            {
                "id": 1026,
                "name": "The Legend of Zelda: Breath of the Wild",
                "first_release_date": 1485907200,
                "cover": {"id": 12345, "url": "//images.igdb.com/igdb/image/upload/t_thumb/co1r0c.jpg"},
                "summary": "Forget everything you know about The Legend of Zelda games.",
                "genres": [{"id": 31, "name": "Action-Adventure"}],
                "platforms": [{"id": 6, "name": "Nintendo Switch"}],
            }
        ]
        responses.post(
            "https://api.igdb.com/v4/games",
            json=mock_games,
            status=200,
        )

        client = IGDBClient("test_client_id", "test_client_secret")
        game = client.get_game(1026)

        assert isinstance(game, dict)
        assert game["id"] == 1026
        assert game["name"] == "The Legend of Zelda: Breath of the Wild"
        assert game["first_release_date"] == 1485907200
        assert game["cover"]["url"] == "//images.igdb.com/igdb/image/upload/t_thumb/co1r0c.jpg"
        assert game["summary"] == "Forget everything you know about The Legend of Zelda games."
        assert game["genres"] == [{"id": 31, "name": "Action-Adventure"}]
        assert game["platforms"] == [{"id": 6, "name": "Nintendo Switch"}]

        # Verify the request body contains the game ID
        req = responses.calls[1].request
        assert req.url == "https://api.igdb.com/v4/games"
        assert "where id = 1026" in req.body

    @responses.activate
    def test_token_caching(self):
        """Test that the token is cached and not re-fetched on every request."""
        # Mock token endpoint (will only be called once)
        responses.post(
            "https://id.twitch.tv/oauth2/token",
            json={
                "access_token": "cached_token",
                "expires_in": 3600,
                "token_type": "bearer",
            },
            status=200,
        )

        # Mock two separate game searches
        def game_callback(request):
            return (200, {}, '[]')

        responses.post(
            "https://api.igdb.com/v4/games",
            json=[],
            status=200,
        )
        responses.post(
            "https://api.igdb.com/v4/games",
            json=[],
            status=200,
        )

        client = IGDBClient("test_client_id", "test_client_secret")
        client.search_games("mario")
        client.search_games("zelda")

        # Token endpoint should only be called once
        token_calls = [
            c for c in responses.calls
            if c.request.url == "https://id.twitch.tv/oauth2/token"
        ]
        assert len(token_calls) == 1

    @responses.activate
    def test_search_returns_empty_list_on_no_results(self):
        """Test that search returns an empty list when no games match."""
        responses.post(
            "https://id.twitch.tv/oauth2/token",
            json={"access_token": "tok", "expires_in": 3600, "token_type": "bearer"},
            status=200,
        )
        responses.post(
            "https://api.igdb.com/v4/games",
            json=[],
            status=200,
        )

        client = IGDBClient("test_client_id", "test_client_secret")
        results = client.search_games("zzzznonexistent")
        assert results == []
