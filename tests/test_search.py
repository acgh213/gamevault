"""Tests for search autocomplete: API endpoint and page rendering."""

import pytest
import responses


class TestSearchAPI:
    """Tests for the /api/search JSON endpoint used by autocomplete."""

    @responses.activate
    def test_api_search_returns_json(self, client):
        """Test that the API search endpoint returns a JSON list."""
        # Mock IGDB auth token endpoint
        responses.post(
            "https://id.twitch.tv/oauth2/token",
            json={"access_token": "test_token", "expires_in": 3600, "token_type": "bearer"},
            status=200,
        )
        # Mock IGDB games search
        responses.post(
            "https://api.igdb.com/v4/games",
            json=[
                {
                    "id": 1026,
                    "name": "The Legend of Zelda: Ocarina of Time",
                    "cover": {"url": "//images.igdb.com/cover.jpg"},
                    "summary": "A classic adventure game.",
                }
            ],
            status=200,
        )

        response = client.get("/api/search?q=zelda")
        assert response.status_code == 200
        assert response.content_type and "json" in response.content_type
        data = response.get_json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "name" in data[0]

    def test_api_search_min_query_length(self, client):
        """Test that empty query returns empty JSON list immediately (no IGDB call)."""
        response = client.get("/api/search?q=")
        assert response.status_code == 200
        data = response.get_json()
        assert data == []

    def test_api_search_no_query_param(self, client):
        """Test that missing query param returns empty JSON list."""
        response = client.get("/api/search")
        assert response.status_code == 200
        data = response.get_json()
        assert data == []


class TestSearchPage:
    """Tests for the search page template rendering."""

    def test_search_page_renders(self, client):
        """Test that the search page renders successfully."""
        response = client.get("/search")
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert "Search Games" in html
        # Should include the search input
        assert 'name="q"' in html or 'name="q"' in response.data

    def test_search_page_with_query(self, client):
        """Test search page with a query parameter renders."""
        response = client.get("/search?q=mario")
        assert response.status_code == 200
