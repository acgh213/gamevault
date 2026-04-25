"""Tests for the authentication system."""
import pytest
from werkzeug.security import check_password_hash


class TestAuthRegister:
    """Tests for register_user."""

    def test_register_creates_user(self, db, app):
        """Test that register_user creates a new user with hashed password."""
        from auth import register_user
        from models import User

        with app.app_context():
            user = register_user("newuser", "new@example.com", "securepass123")

            assert user is not None
            assert user.username == "newuser"
            assert user.email == "new@example.com"
            # Password should be hashed, not plaintext
            assert user.password_hash != "securepass123"
            assert check_password_hash(user.password_hash, "securepass123") is True

    def test_register_duplicate_username_fails(self, db, app):
        """Test that registering with an existing username raises an exception."""
        from auth import register_user
        from models import User

        with app.app_context():
            register_user("dupuser", "first@example.com", "password1")

            with pytest.raises(Exception):
                register_user("dupuser", "second@example.com", "password2")


class TestAuthAuthenticate:
    """Tests for authenticate_user."""

    def test_authenticate_valid_credentials(self, db, app):
        """Test that valid credentials return the user."""
        from auth import register_user, authenticate_user

        with app.app_context():
            register_user("validuser", "valid@example.com", "mypassword")

            user = authenticate_user("validuser", "mypassword")
            assert user is not None
            assert user.username == "validuser"

    def test_authenticate_invalid_password(self, db, app):
        """Test that invalid password returns None."""
        from auth import register_user, authenticate_user

        with app.app_context():
            register_user("validuser2", "valid2@example.com", "correctpassword")

            user = authenticate_user("validuser2", "wrongpassword")
            assert user is None


class TestAuthLoginRequired:
    """Tests for the login_required decorator."""

    def test_login_required_redirects(self, app, client):
        """Test that accessing a protected route redirects to login."""
        from auth import login_required

        # Register a dummy login route so url_for("login") resolves
        @app.route("/login")
        def login():
            return "Login page"

        # Register a protected route for testing
        @app.route("/protected")
        @login_required
        def protected_view():
            return "You're in!"

        # Make request without being logged in
        response = client.get("/protected", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location
