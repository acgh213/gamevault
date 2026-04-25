"""Authentication module for GameVault.

Provides functions for user registration, authentication, and a
login_required decorator for protecting Flask routes.
"""
from functools import wraps

from flask import redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models import User


def register_user(username, email, password):
    """Create a new user with a hashed password.

    Args:
        username: The desired username (must be unique).
        email: The user's email address (must be unique).
        password: The plaintext password (will be hashed before storage).

    Returns:
        The newly created User instance.

    Raises:
        Exception: If the username or email already exists (SQLAlchemy
            integrity error bubbles up).
    """
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
    )
    return user.save()


def authenticate_user(username, password):
    """Verify a user's credentials.

    Looks up a user by username and checks the password against the
    stored hash.

    Args:
        username: The username to look up.
        password: The plaintext password to verify.

    Returns:
        The User instance if credentials are valid, or None if the user
        does not exist or the password is incorrect.
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        return None
    if not check_password_hash(user.password_hash, password):
        return None
    return user


def login_required(view_func):
    """Decorator that requires the user to be logged in.

    Checks for a 'user_id' key in the Flask session. If it is missing
    the request is redirected to the login page.

    Usage::

        @app.route("/protected")
        @login_required
        def protected_view():
            return "You're in!"
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view
