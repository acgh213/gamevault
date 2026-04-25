"""Flask routes blueprint for GameVault."""

from datetime import datetime

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from auth import authenticate_user, login_required, register_user
from igdb import IGDBClient
from models import Game, Review, User, db

routes = Blueprint("routes", __name__)


def _get_igdb_client(app=None):
    """Get an IGDB client from app config."""
    if app is None:
        from flask import current_app

        app = current_app
    return IGDBClient(
        app.config.get("IGDB_CLIENT_ID", ""),
        app.config.get("IGDB_CLIENT_SECRET", ""),
    )


def _format_igdb_game(raw):
    """Format an IGDB game dict into a cleaner structure for templates."""
    cover_url = None
    if raw.get("cover") and raw["cover"].get("url"):
        cover_url = raw["cover"]["url"]
        if cover_url.startswith("//"):
            cover_url = "https:" + cover_url
        # Use large thumbnails instead of tiny ones
        cover_url = cover_url.replace("t_thumb", "t_cover_big")

    genres = []
    if raw.get("genres"):
        genres = [g["name"] for g in raw["genres"]]

    platforms = []
    if raw.get("platforms"):
        platforms = [p["name"] for p in raw["platforms"]]

    release_date = None
    if raw.get("first_release_date"):
        try:
            release_date = datetime.fromtimestamp(raw["first_release_date"]).strftime(
                "%B %d, %Y"
            )
        except (OSError, ValueError, OverflowError):
            release_date = str(raw["first_release_date"])

    return {
        "id": raw["id"],
        "name": raw.get("name", "Unknown"),
        "cover_url": cover_url,
        "summary": raw.get("summary", ""),
        "genres": genres,
        "platforms": platforms,
        "release_date": release_date,
    }


# ─── HTML Routes ──────────────────────────────────────────────────────────────


@routes.route("/")
def home():
    """Home page with recent reviews and featured content."""
    recent_reviews = (
        Review.query.order_by(Review.created_at.desc()).limit(12).all()
    )
    return render_template("index.html", recent_reviews=recent_reviews)


@routes.route("/login", methods=["GET", "POST"])
def login():
    """Login page -- form submission authenticates user."""
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = authenticate_user(username, password)
        if user is not None:
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("routes.home"))
        error = "Invalid username or password."

    return render_template("login.html", error=error)


@routes.route("/register", methods=["GET", "POST"])
def register():
    """Registration page -- form submission creates a new user."""
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            error = "All fields are required."
        else:
            try:
                user = register_user(username, email, password)
                session["user_id"] = user.id
                session["username"] = user.username
                return redirect(url_for("routes.home"))
            except Exception:
                error = "Username or email already taken."

    return render_template("login.html", error=error, is_register=True)


@routes.route("/logout")
def logout():
    """Log out the current user by clearing the session."""
    session.clear()
    return redirect(url_for("routes.home"))


@routes.route("/search")
def search():
    """Game search page -- queries IGDB and displays results."""
    query = request.args.get("q", "").strip()
    results = []
    if query:
        try:
            igdb = _get_igdb_client()
            raw_results = igdb.search_games(query, limit=20)
            results = [_format_igdb_game(g) for g in raw_results]
        except Exception:
            results = []
    return render_template("search.html", query=query, results=results)


@routes.route("/game/<int:igdb_id>")
def game_detail(igdb_id):
    """Game detail page -- shows info, cover, and reviews."""
    game_data = None
    error = None
    try:
        igdb = _get_igdb_client()
        raw = igdb.get_game(igdb_id)
        if raw is None:
            error = "Game not found."
        else:
            game_data = _format_igdb_game(raw)
    except Exception as e:
        error = f"Could not load game data: {e}"

    # Find or create the Game in our DB
    db_game = Game.query.filter_by(igdb_id=igdb_id).first()
    if db_game is None and game_data:
        db_game = Game(
            igdb_id=game_data["id"],
            name=game_data["name"],
            cover_url=game_data["cover_url"],
            summary=game_data["summary"],
            genres=game_data["genres"],
            platforms=game_data["platforms"],
            release_date=game_data["release_date"],
        )
        db.session.add(db_game)
        db.session.commit()

    reviews = []
    if db_game:
        reviews = (
            Review.query.filter_by(game_id=db_game.id)
            .order_by(Review.created_at.desc())
            .all()
        )

    return render_template(
        "game.html", game=game_data, reviews=reviews, error=error
    )


@routes.route("/profile/<username>")
def profile(username):
    """User profile page with stats and recent reviews."""
    user = User.query.filter_by(username=username).first()
    if user is None:
        return render_template("404.html"), 404

    reviews = (
        Review.query.filter_by(user_id=user.id)
        .order_by(Review.created_at.desc())
        .limit(20)
        .all()
    )

    # Build stats
    total_reviews = Review.query.filter_by(user_id=user.id).count()
    avg_rating = db.session.query(db.func.avg(Review.rating)).filter(
        Review.user_id == user.id
    ).scalar()

    return render_template(
        "profile.html",
        profile_user=user,
        reviews=reviews,
        total_reviews=total_reviews,
        avg_rating=round(avg_rating, 1) if avg_rating else None,
    )


# ─── API Routes ───────────────────────────────────────────────────────────────


@routes.route("/api/search")
def api_search():
    """JSON search endpoint -- returns a list of matching games."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    try:
        igdb = _get_igdb_client()
        raw_results = igdb.search_games(query, limit=10)
        results = [_format_igdb_game(g) for g in raw_results]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/api/reviews/<int:igdb_id>", methods=["GET"])
def api_get_reviews(igdb_id):
    """Get reviews for a game by IGDB ID."""
    db_game = Game.query.filter_by(igdb_id=igdb_id).first()
    if db_game is None:
        return jsonify([])

    reviews = (
        Review.query.filter_by(game_id=db_game.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return jsonify(
        [
            {
                "id": r.id,
                "user_id": r.user_id,
                "username": r.author.username,
                "rating": r.rating,
                "body": r.body,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reviews
        ]
    )


@routes.route("/api/reviews", methods=["POST"])
@login_required
def api_create_review():
    """Create a review for a game (login required)."""
    data = request.get_json(silent=True) or {}
    igdb_id = data.get("igdb_id")
    rating = data.get("rating")
    body = data.get("body", "")

    if not igdb_id or not rating:
        return jsonify({"error": "igdb_id and rating are required"}), 400

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return jsonify({"error": "rating must be an integer"}), 400

    if rating < 1 or rating > 5:
        return jsonify({"error": "rating must be between 1 and 5"}), 400

    # Find or create game in DB
    db_game = Game.query.filter_by(igdb_id=igdb_id).first()
    if db_game is None:
        # Try to fetch game data from IGDB
        try:
            igdb = _get_igdb_client()
            raw = igdb.get_game(igdb_id)
            if raw:
                game_data = _format_igdb_game(raw)
                db_game = Game(
                    igdb_id=game_data["id"],
                    name=game_data["name"],
                    cover_url=game_data["cover_url"],
                    summary=game_data["summary"],
                    genres=game_data["genres"],
                    platforms=game_data["platforms"],
                    release_date=game_data["release_date"],
                )
                db.session.add(db_game)
                db.session.commit()
            else:
                # Create a minimal game entry
                db_game = Game(igdb_id=igdb_id, name=f"Game #{igdb_id}")
                db.session.add(db_game)
                db.session.commit()
        except Exception:
            db_game = Game(igdb_id=igdb_id, name=f"Game #{igdb_id}")
            db.session.add(db_game)
            db.session.commit()

    # Check for duplicate review
    existing = Review.query.filter_by(
        user_id=session["user_id"], game_id=db_game.id
    ).first()
    if existing:
        return jsonify({"error": "You have already reviewed this game"}), 409

    review = Review(
        user_id=session["user_id"],
        game_id=db_game.id,
        rating=rating,
        body=body,
    )
    try:
        review.save()
        return jsonify(
            {
                "id": review.id,
                "user_id": review.user_id,
                "rating": review.rating,
                "body": review.body,
                "created_at": review.created_at.isoformat()
                if review.created_at
                else None,
            }
        ), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Could not create review"}), 500
