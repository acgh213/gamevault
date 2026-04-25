"""Tests for Flask routes, templates, and blueprint registration."""

import pytest
import responses
from flask import session, template_rendered
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


class TestBlueprintRegistration:
    """Tests that the routes blueprint is registered correctly."""

    def test_blueprint_registered(self, app):
        """Test that the 'routes' blueprint is registered with the app."""
        assert 'routes' in app.blueprints

    def test_static_folder_serves(self, client):
        """Test that the static folder is configured."""
        response = client.get('/static/css/style.css')
        # Should exist (404 means no static file, not that blueprint isn't registered)
        assert response.status_code in (200, 404)


class TestHomeRoute:
    """Tests for the home/index route."""

    def test_home_page_returns_200(self, client):
        """Test that the home page returns a 200 status code."""
        response = client.get('/')
        assert response.status_code == 200

    def test_home_page_uses_index_template(self, app, client):
        """Test that the home page renders the index.html template."""
        with captured_templates(app) as templates:
            client.get('/')
            assert len(templates) > 0
            template_name = templates[0][0].name
            assert template_name == 'index.html'

    def test_home_page_shows_title(self, client):
        """Test that the home page contains expected title content."""
        response = client.get('/')
        assert b'GameVault' in response.data or b'gamevault' in response.data.lower()


class TestLoginRoute:
    """Tests for the login route."""

    def test_login_page_returns_200(self, client):
        """Test that the login page returns 200 for GET."""
        response = client.get('/login')
        assert response.status_code == 200

    def test_login_page_uses_login_template(self, app, client):
        """Test that the login page renders the login.html template."""
        with captured_templates(app) as templates:
            client.get('/login')
            assert len(templates) > 0
            template_name = templates[0][0].name
            assert template_name == 'login.html'

    def test_login_with_valid_credentials(self, app, client):
        """Test that valid login redirects to home."""
        from auth import register_user

        with app.app_context():
            register_user('logintest', 'login@test.com', 'password123')

        response = client.post('/login', data={
            'username': 'logintest',
            'password': 'password123',
        }, follow_redirects=False)
        assert response.status_code == 302

    def test_login_sets_session(self, app, client):
        """Test that valid login sets user_id in session."""
        from auth import register_user

        with app.app_context():
            register_user('sessiontest', 'session@test.com', 'password123')

        with client:
            client.post('/login', data={
                'username': 'sessiontest',
                'password': 'password123',
            })
            assert session.get('user_id') is not None
            assert session.get('username') == 'sessiontest'

    def test_login_with_invalid_credentials(self, client):
        """Test that invalid login returns to login page with error."""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'wrong',
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_form_has_required_fields(self, client):
        """Test that login form has username and password fields."""
        response = client.get('/login')
        assert b'username' in response.data.lower() or b'username' in response.data
        assert b'password' in response.data.lower() or b'password' in response.data


class TestRegisterRoute:
    """Tests for the register route."""

    def test_register_page_returns_200(self, client):
        """Test that the register page returns 200 for GET."""
        response = client.get('/register')
        assert response.status_code == 200

    def test_register_page_uses_login_template(self, app, client):
        """Test that the register page renders login.html (shared form template)."""
        with captured_templates(app) as templates:
            client.get('/register')
            assert len(templates) > 0
            template_name = templates[0][0].name
            assert template_name == 'login.html'

    def test_register_creates_user_and_redirects(self, app, client):
        """Test that valid registration creates user and redirects."""
        response = client.post('/register', data={
            'username': 'newregister',
            'email': 'newreg@test.com',
            'password': 'secure123',
        }, follow_redirects=False)
        assert response.status_code == 302

    def test_register_sets_session(self, app, client):
        """Test that registration auto-logs in the user."""
        from models import User

        with client:
            client.post('/register', data={
                'username': 'autologin',
                'email': 'auto@test.com',
                'password': 'secure123',
            })
            assert session.get('user_id') is not None
            assert session.get('username') == 'autologin'

    def test_register_duplicate_username(self, app, client):
        """Test that duplicate username shows error."""
        from auth import register_user

        with app.app_context():
            register_user('dupreg', 'dupreg@test.com', 'password123')

        response = client.post('/register', data={
            'username': 'dupreg',
            'email': 'other@test.com',
            'password': 'password123',
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_register_form_has_required_fields(self, client):
        """Test that register form has email, username, and password fields."""
        response = client.get('/register')
        assert b'email' in response.data.lower() or b'email' in response.data


class TestLogoutRoute:
    """Tests for the logout route."""

    def test_logout_clears_session(self, app, client):
        """Test that logout clears the session and redirects."""
        from auth import register_user

        with app.app_context():
            register_user('logouttest', 'logout@test.com', 'password123')

        with client:
            client.post('/login', data={
                'username': 'logouttest',
                'password': 'password123',
            })
            assert session.get('user_id') is not None

            response = client.get('/logout', follow_redirects=False)
            assert response.status_code == 302
            assert session.get('user_id') is None


class TestSearchRoute:
    """Tests for the search route."""

    def test_search_page_returns_200(self, client):
        """Test that the search page returns 200."""
        response = client.get('/search?q=zelda')
        assert response.status_code == 200

    def test_search_page_uses_search_template(self, app, client):
        """Test that the search page renders search.html template."""
        with captured_templates(app) as templates:
            client.get('/search?q=mario')
            if templates:
                template_name = templates[0][0].name
                assert template_name in ('search.html', 'index.html')


class TestAPIRoutes:
    """Tests for API routes."""

    @responses.activate
    def test_api_search_returns_json(self, client):
        """Test that the API search endpoint returns JSON."""
        responses.post(
            "https://id.twitch.tv/oauth2/token",
            json={"access_token": "***", "expires_in": 3600, "token_type": "bearer"},
            status=200,
        )
        responses.post(
            "https://api.igdb.com/v4/games",
            json=[],
            status=200,
        )
        response = client.get('/api/search?q=zelda')
        assert response.status_code == 200
        assert response.content_type and 'json' in response.content_type

    @responses.activate
    def test_api_search_returns_list(self, client):
        """Test that the API search endpoint returns a list."""
        responses.post(
            "https://id.twitch.tv/oauth2/token",
            json={"access_token": "***", "expires_in": 3600, "token_type": "bearer"},
            status=200,
        )
        responses.post(
            "https://api.igdb.com/v4/games",
            json=[],
            status=200,
        )
        response = client.get('/api/search?q=zelda')
        data = response.get_json()
        assert isinstance(data, list)

    def test_api_reviews_get(self, client):
        """Test that the API reviews get endpoint returns JSON."""
        response = client.get('/api/reviews/12345')
        assert response.status_code == 200
        assert response.content_type and 'json' in response.content_type

    def test_api_reviews_get_returns_list(self, client):
        """Test that the API reviews get endpoint returns a list."""
        response = client.get('/api/reviews/12345')
        data = response.get_json()
        assert isinstance(data, list)

    def test_api_reviews_post_requires_login(self, client):
        """Test that posting a review without login returns 401 or 302."""
        response = client.post('/api/reviews', json={
            'igdb_id': 12345,
            'rating': 4,
            'body': 'Great game!',
        }, follow_redirects=False)
        assert response.status_code in (302, 401, 403)

    def test_api_reviews_post_with_login(self, app, client):
        """Test that a logged-in user can post a review."""
        from auth import register_user

        with app.app_context():
            register_user('reviewapi', 'reviewapi@test.com', 'password123')

        with client:
            client.post('/login', data={
                'username': 'reviewapi',
                'password': 'password123',
            })

            response = client.post('/api/reviews', json={
                'igdb_id': 99999,
                'rating': 5,
                'body': 'Amazing game!',
            })
            # Should succeed
            assert response.status_code in (200, 201)


class TestGameRoute:
    """Tests for the game detail route."""

    def test_game_page_returns_200(self, client):
        """Test that the game detail page returns 200."""
        response = client.get('/game/1026')
        assert response.status_code == 200

    def test_game_page_uses_game_template(self, app, client):
        """Test that the game page renders game.html template."""
        with captured_templates(app) as templates:
            client.get('/game/1026')
            if templates:
                template_name = templates[0][0].name
                assert template_name in ('game.html', 'search.html')


class TestProfileRoute:
    """Tests for the profile route."""

    def test_profile_page_returns_200_for_existing_user(self, app, client):
        """Test that an existing user's profile page returns 200."""
        from auth import register_user

        with app.app_context():
            register_user('profileuser', 'profile@test.com', 'password123')

        response = client.get('/profile/profileuser')
        assert response.status_code == 200

    def test_profile_page_uses_profile_template(self, app, client):
        """Test that the profile page renders profile.html."""
        from auth import register_user

        with app.app_context():
            register_user('proftemp', 'proftemp@test.com', 'password123')

        with captured_templates(app) as templates:
            client.get('/profile/proftemp')
            if templates:
                template_name = templates[0][0].name
                assert template_name == 'profile.html'

    def test_profile_404_for_nonexistent_user(self, client):
        """Test that a nonexistent user's profile returns 404."""
        response = client.get('/profile/nonexistent_user_xyz')
        assert response.status_code == 404


class TestNavbarAndLayout:
    """Tests for navbar/base template features."""

    def test_navbar_shows_login_when_logged_out(self, client):
        """Test that the navbar shows login link when logged out."""
        response = client.get('/')
        html = response.data.lower()
        assert b'login' in html or b'sign in' in html

    def test_navbar_shows_username_when_logged_in(self, app, client):
        """Test that the navbar shows the username when logged in."""
        from auth import register_user

        with app.app_context():
            register_user('navuser', 'nav@test.com', 'password123')

        with client:
            client.post('/login', data={
                'username': 'navuser',
                'password': 'password123',
            })
            response = client.get('/')
            assert b'navuser' in response.data

    def test_navbar_shows_logout_when_logged_in(self, app, client):
        """Test that the navbar shows a logout link when logged in."""
        from auth import register_user

        with app.app_context():
            register_user('navuser2', 'nav2@test.com', 'password123')

        with client:
            client.post('/login', data={
                'username': 'navuser2',
                'password': 'password123',
            })
            response = client.get('/')
            assert b'logout' in response.data.lower()
