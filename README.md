# GameVault

**A Letterboxd for games** — track, rate, review, and discover video games. GameVault is a full-featured Flask web application that lets you build a personal game library, write reviews, curate custom lists, and explore what the community is playing. Powered by the [IGDB API](https://igdb.com) for rich, up-to-date game data.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-92%20passing-brightgreen)](#testing)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.1-000)](https://flask.palletsprojects.com/)

---

## Features

### 🔍 Game Search
Search thousands of games from the IGDB database with cover art, genres, platforms, and release dates. Rich detail pages show summaries, metadata, and community reviews.

### ⭐ Reviews & Ratings
Rate games on a 1–5 star scale and write detailed reviews. Every game page shows community reviews, and the home page highlights recent activity.

### 📋 Curated Lists
Create custom game lists (e.g. "Favorites", "Backlog", "Completed") and organize your collection. Add or remove games with a click — all managed via interactive modals and dropdowns.

### 👤 User Profiles
Every user gets a profile page showing their stats — total reviews, average rating, unique games played — plus their recent reviews and curated lists.

### 🌙 Dark Theme
A polished, hand-crafted dark theme with gold accents, smooth transitions, and responsive design that looks great on desktop and mobile.

### 🔐 Authentication
Secure user registration and login with password hashing (Werkzeug) and session-based auth. Protected API routes ensure only logged-in users can create reviews and manage lists.

### 📱 Responsive Design
Mobile-first responsive layout with a collapsible navigation menu, adaptive grids, and touch-friendly interactions.

---

## Screenshots

| Home Page | Game Detail | User Profile |
|-----------|-------------|--------------|
| ![Home Page](https://via.placeholder.com/400x250?text=GameVault+Home) | ![Game Detail](https://via.placeholder.com/400x250?text=Game+Detail) | ![Profile](https://via.placeholder.com/400x250?text=Profile) |

| Search Results | Game Lists | Dark Theme |
|----------------|------------|------------|
| ![Search](https://via.placeholder.com/400x250?text=Search) | ![Lists](https://via.placeholder.com/400x250?text=Lists) | ![Dark Theme](https://via.placeholder.com/400x250?text=Dark+Theme) |

> **Note:** Replace the placeholder images above with actual screenshots of your running instance.

---

## Architecture

```
gamevault/
├── app.py                  # Flask application factory
├── config.py               # Configuration (DB, IGDB keys, secret key)
├── models.py               # SQLAlchemy models (User, Game, Review, GameList)
├── routes.py               # Flask blueprint with HTML + JSON API routes
├── auth.py                 # Authentication (register, login, login_required decorator)
├── igdb.py                 # IGDB API client (OAuth2, search, game lookup)
├── requirements.txt        # Python dependencies
├── start.sh                # Production startup script
├── static/
│   ├── css/
│   │   └── style.css       # Full dark-theme stylesheet (1850+ lines)
│   └── js/
│       ├── review.js       # Review form submission (AJAX)
│       ├── lists.js        # List create/manage modals (AJAX)
│       └── search.js       # Autocomplete search
├── templates/
│   ├── base.html           # Base layout (nav, footer, dark theme)
│   ├── index.html          # Home page with recent reviews
│   ├── search.html         # Game search with grid results
│   ├── game.html           # Game detail page (info, reviews, list dropdown)
│   ├── profile.html        # User profile (stats, reviews, lists)
│   ├── lists.html          # User's game lists management
│   ├── login.html          # Login / Register form
│   └── 404.html            # Custom 404 page
├── tests/
│   ├── conftest.py         # Pytest fixtures (app, client, db)
│   ├── test_auth.py        # Authentication tests
│   ├── test_igdb.py        # IGDB API client tests
│   ├── test_lists_api.py   # List API endpoint tests
│   ├── test_models.py      # Model validation tests
│   ├── test_profile.py     # Profile page tests
│   ├── test_responsive.py  # Responsive design tests
│   ├── test_reviews_api.py # Review API endpoint tests
│   ├── test_routes.py      # Route/page rendering tests
│   └── test_search.py      # Search functionality tests
└── instance/
    └── gamevault.db        # SQLite database (created at runtime)
```

### Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+, Flask 3.1 |
| **Database** | SQLAlchemy ORM + SQLite |
| **Templating** | Jinja2 (server-side rendering) |
| **Frontend** | HTML5, CSS3 (custom dark theme), vanilla JavaScript |
| **Game Data** | IGDB API v4 (Twitch OAuth2) |
| **Auth** | Werkzeug password hashing + Flask session cookies |
| **Testing** | pytest 9.0, pytest-flask, responses (HTTP mocking) |
| **Deployment** | Gunicorn / Werkzeug on Linux |

### Data Model

**User** — `id`, `username`, `email`, `password_hash`, `created_at`
- Has many reviews and game lists

**Game** — `id`, `igdb_id` (unique), `name`, `release_date`, `cover_url`, `summary`, `genres` (JSON), `platforms` (JSON), `created_at`
- Has many reviews; belongs to many lists (M2M via `list_games`)

**Review** — `id`, `user_id`, `game_id`, `rating` (1–5, validated), `body`, `created_at`, `updated_at`
- Unique constraint per user+game (one review per game per user)

**GameList** — `id`, `user_id`, `name`, `description`, `is_public`, `created_at`
- Many-to-many with Game via `list_games` join table

---

## Setup

### Prerequisites

- Python 3.11+
- Git
- (Optional) [IGDB API](https://api.igdb.com/) credentials for game search

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/acgh213/gamevault.git
   cd gamevault
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database:**

   ```bash
   python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

5. **Configure IGDB API credentials** (optional — search needs these):

   ```bash
   export IGDB_CLIENT_ID="your_twitch_client_id"
   export IGDB_CLIENT_SECRET="your_twitch_client_secret"
   ```

   You can also set them in `config.py` directly. Get credentials by registering an application on the [Twitch Developer Portal](https://dev.twitch.tv/console).

### Running

**Development:**

```bash
cd gamevault
source venv/bin/activate
export FLASK_APP=app.py
export FLASK_DEBUG=1
python -m flask run --host=0.0.0.0 --port=8891
```

**Production:**

```bash
./start.sh
```

The app will be available at `http://localhost:8891`.

### Testing

Run the full test suite (92 tests):

```bash
python -m pytest
```

Run with coverage:

```bash
python -m pytest -v
```

Run specific test files:

```bash
python -m pytest tests/test_auth.py tests/test_models.py -v
```

---

## API Documentation

GameVault exposes a set of JSON API endpoints for search, reviews, and list management.

### Search

#### `GET /api/search`

Search for games by name via IGDB.

**Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Game name to search for |

**Response:** `200 OK`

```json
[
  {
    "id": 1020,
    "name": "The Legend of Zelda: Breath of the Wild",
    "cover_url": "https://images.igdb.com/.../co1wyy.jpg",
    "summary": "Forget everything you know...",
    "genres": ["Adventure", "Role-playing (RPG)"],
    "platforms": ["Nintendo Switch", "Wii U"],
    "release_date": "March 3, 2017"
  }
]
```

**Response:** `500 Internal Server Error`

```json
{
  "error": "Could not connect to IGDB"
}
```

### Reviews

#### `GET /api/reviews/<igdb_id>`

Get all reviews for a game by its IGDB ID.

**Response:** `200 OK`

```json
[
  {
    "id": 42,
    "user_id": 1,
    "username": "gamer42",
    "rating": 4,
    "body": "An absolutely stunning experience.",
    "created_at": "2025-04-20T14:30:00"
  }
]
```

#### `POST /api/reviews`

Create a review for a game. Requires authentication (session cookie).

**Request Body:**

```json
{
  "igdb_id": 1020,
  "rating": 4,
  "body": "A masterpiece of game design."
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `igdb_id` | integer | Yes | IGDB game ID |
| `rating` | integer | Yes | Rating 1–5 |
| `body` | string | No | Review text |

**Response:** `201 Created`

```json
{
  "id": 43,
  "user_id": 1,
  "rating": 4,
  "body": "A masterpiece of game design.",
  "created_at": "2025-04-25T10:00:00"
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `400` | Missing or invalid fields |
| `409` | User already reviewed this game |
| `500` | Server error |

### Lists

#### `POST /api/lists`

Create a new game list. Requires authentication.

**Request Body:**

```json
{
  "name": "Favorites",
  "description": "My all-time favorite games"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | List name |
| `description` | string | No | Optional description |

**Response:** `201 Created`

```json
{
  "id": 1,
  "name": "Favorites",
  "description": "My all-time favorite games",
  "created_at": "2025-04-25T10:00:00"
}
```

#### `POST /api/lists/<list_id>/games`

Add a game to a list. Requires authentication (must own the list).

**Request Body:**

```json
{
  "game_id": 5
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `game_id` | integer | Yes | Internal Game ID (from DB) |

**Response:** `200 OK`

```json
{
  "message": "Added The Legend of Zelda to Favorites"
}
```

#### `DELETE /api/lists/<list_id>/games/<game_id>`

Remove a game from a list. Requires authentication (must own the list).

**Response:** `200 OK`

```json
{
  "message": "Removed The Legend of Zelda from Favorites"
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| `403` | User does not own this list |
| `404` | List or game not found |
| `409` | Game already in list |

---

## Configuration

Configuration is managed through environment variables and `config.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-key-change-in-production` | Flask session secret |
| `DATABASE_URL` | `sqlite:///gamevault.db` | SQLAlchemy database URI |
| `IGDB_CLIENT_ID` | `""` | Twitch/IGDB API client ID |
| `IGDB_CLIENT_SECRET` | `""` | Twitch/IGDB API client secret |

> ⚠️ **Security:** Change `SECRET_KEY` to a strong random value in production. Never commit real API credentials to version control.

---

## Deployment

### Quick Start (Linux)

```bash
git clone https://github.com/acgh213/gamevault.git ~/gamevault
cd ~/gamevault
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
export FLASK_APP=app.py
export FLASK_ENV=production
python -m flask run --host=0.0.0.0 --port=8891
```

### Using `start.sh`

The included `start.sh` script handles activation and environment setup:

```bash
chmod +x start.sh
./start.sh
```

### Production Considerations

- Use **Gunicorn** instead of Werkzeug for production: `gunicorn -w 4 'app:create_app()' -b 0.0.0.0:8891`
- Set a strong `SECRET_KEY` via environment variable
- Configure IGDB credentials for game search functionality
- Consider using PostgreSQL instead of SQLite for multi-user deployments
- Set up a reverse proxy (Nginx/Caddy) for SSL termination

---

## Test Suite

92 tests across 9 test files, all passing:

| File | Tests | Coverage |
|------|-------|----------|
| `test_auth.py` | Registration, login, logout, session handling | ✅ |
| `test_igdb.py` | IGDB API client, token caching, search, game lookup | ✅ |
| `test_lists_api.py` | Create lists, add/remove games, permissions | ✅ |
| `test_models.py` | Model validation, constraints, relationships | ✅ |
| `test_profile.py` | Profile rendering, stats, edge cases (missing user) | ✅ |
| `test_responsive.py` | Mobile viewport, responsive layout checks | ✅ |
| `test_reviews_api.py` | Create reviews, duplicates, validation, auth requirements | ✅ |
| `test_routes.py` | Home page, login, search rendering | ✅ |
| `test_search.py` | Search page rendering, query handling, edge cases | ✅ |

---

## Roadmap

- [ ] User avatars and bio
- [ ] Social features (follow users, activity feed)
- [ ] Game recommendations based on ratings
- [ ] Public/private list toggles
- [ ] Comment threads on reviews
- [ ] Rich text editor for reviews
- [ ] Admin dashboard
- [ ] PostgreSQL support
- [ ] Docker deployment
- [ ] OAuth login (Discord, GitHub)

---

## Acknowledgments

- **[IGDB](https://igdb.com)** — Video game database and API
- **[Twitch](https://dev.twitch.tv/)** — OAuth2 authentication for IGDB API
- **[Flask](https://flask.palletsprojects.com/)** — Python web framework
- **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM and database toolkit

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Links

- **GitHub:** [https://github.com/acgh213/gamevault](https://github.com/acgh213/gamevault)
- **Deployment:** [https://hermes-sera.exe.xyz:8891](https://hermes-sera.exe.xyz:8891)
