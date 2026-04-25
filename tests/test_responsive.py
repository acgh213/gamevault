"""Tests for responsive CSS loading and structure."""

import pytest


class TestCSSLoading:
    """Tests that the CSS file loads properly via Flask static serving."""

    def test_css_file_serves(self, client):
        """Test that style.css is served from the static folder."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        assert response.content_type in (
            'text/css; charset=utf-8',
            'text/css',
        )

    def test_css_contains_media_queries(self, client):
        """Test that the CSS file contains responsive media query breakpoints."""
        css = client.get('/static/css/style.css').data.decode('utf-8')
        assert '@media (max-width: 768px)' in css
        assert '@media (max-width: 480px)' in css

    def test_css_contains_gold_accent(self, client):
        """Test that the CSS file uses the expected accent color variable."""
        css = client.get('/static/css/style.css').data.decode('utf-8')
        assert '--accent-gold' in css

    def test_css_has_games_grid_responsive(self, client):
        """Test that the games grid uses flexible minmax sizing."""
        css = client.get('/static/css/style.css').data.decode('utf-8')
        assert 'minmax(150px' in css

    def test_css_has_navbar_responsive(self, client):
        """Test that the navbar has mobile layout rules."""
        css = client.get('/static/css/style.css').data.decode('utf-8')
        assert 'flex-direction: column' in css

    def test_css_has_scroll_behavior(self, client):
        """Test that smooth scrolling is enabled."""
        css = client.get('/static/css/style.css').data.decode('utf-8')
        assert 'scroll-behavior: smooth' in css

    def test_css_has_focus_states(self, client):
        """Test that focus-visible accessibility styles exist."""
        css = client.get('/static/css/style.css').data.decode('utf-8')
        assert 'focus-visible' in css

    def test_css_has_search_loading(self, client):
        """Test that search loading state styles exist."""
        css = client.get('/static/css/style.css').data.decode('utf-8')
        assert 'search-loading' in css

    def test_css_has_tap_targets(self, client):
        """Test that touch-friendly tap target sizes exist."""
        css = client.get('/static/css/style.css').data.decode('utf-8')
        assert 'min-height: 44px' in css
        assert 'min-width: 44px' in css

    def test_css_has_empty_state(self, client):
        """Test that empty state styling exists."""
        css = client.get('/static/css/style.css').data.decode('utf-8')
        assert '.empty-state' in css

    def test_css_has_profile_stats_stacking(self, client):
        """Test that profile stats stack vertically on mobile."""
        css = client.get('/static/css/style.css').data.decode('utf-8')
        assert 'profile-stats' in css
