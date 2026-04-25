"""IGDB API client for GameVault.

Provides search and lookup functionality for video games
using the IGDB (Internet Game Database) API via Twitch OAuth2 authentication.
"""

import time

import requests


TOKEN_URL = "https://id.twitch.tv/oauth2/token"
API_BASE = "https://api.igdb.com/v4"
FIELDS = (
    "id,name,first_release_date,cover.url,summary,genres.name,platforms.name"
)


class IGDBClient:
    """Client for the IGDB video game database API.

    Handles OAuth2 token acquisition (with caching), game search,
    and single-game lookups.

    Attributes:
        client_id: Twitch/IGDB API client ID.
        client_secret: Twitch/IGDB API client secret.
    """

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: str | None = None
        self._token_expires_at: float | None = None

    def _get_token(self) -> str:
        """Get a valid access token, fetching a new one if expired or absent."""
        if self._token and self._token_expires_at and time.time() < self._token_expires_at:
            return self._token

        resp = requests.post(
            TOKEN_URL,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        # Buffer expiry by 60 seconds to avoid edge cases
        self._token_expires_at = time.time() + data["expires_in"] - 60
        return self._token

    def _headers(self) -> dict:
        """Build the headers required for IGDB API requests."""
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self._get_token()}",
        }

    def _parse_games(self, raw: list[dict]) -> list[dict]:
        """Return raw game data as-is — IGDB already returns it structured."""
        return raw

    def search_games(self, query: str, limit: int = 10) -> list[dict]:
        """Search for games by name.

        Args:
            query: The game name or partial name to search for.
            limit: Maximum number of results to return (default 10).

        Returns:
            A list of parsed game dictionaries with fields:
            id, name, first_release_date, cover.url, summary,
            genres.name, platforms.name.
        """
        body = (
            f'search "{query}";\n'
            f"fields {FIELDS};\n"
            f"limit {limit};\n"
        )
        resp = requests.post(
            f"{API_BASE}/games",
            headers=self._headers(),
            data=body,
            timeout=30,
        )
        resp.raise_for_status()
        return self._parse_games(resp.json())

    def get_game(self, igdb_id: int) -> dict | None:
        """Get a single game by its IGDB ID.

        Args:
            igdb_id: The numeric IGDB game identifier.

        Returns:
            A parsed game dictionary, or None if not found.
        """
        body = (
            f"where id = {igdb_id};\n"
            f"fields {FIELDS};\n"
        )
        resp = requests.post(
            f"{API_BASE}/games",
            headers=self._headers(),
            data=body,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None
        return self._parse_games(data)[0]
