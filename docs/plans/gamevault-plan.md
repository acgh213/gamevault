# GameVault — Letterboxd for Games

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a game database and review site where users can search, rate, review, and catalog games — like Letterboxd but for video games.

**Architecture:** Flask backend with SQLite database, vanilla JS frontend with dark theme. Single-user initially, expandable. IGDB API for game metadata. All served from the exe.dev VM on a high port.

**Tech Stack:** Python 3.11, Flask, SQLite, vanilla JS, IGDB API (free tier), pytest

---

## Project Structure

```
~/gamevault/
├── app.py                  # Flask application
├── config.py               # Configuration (API keys, DB path, etc.)
├── models.py               # SQLAlchemy models
├── requirements.txt        # Python dependencies
├── schema.sql              # SQLite schema
├── tests/
│   ├── conftest.py         # Test fixtures
│   ├── test_models.py      # Model tests
│   ├── test_routes.py      # Route tests
│   ├── test_igdb.py        # IGDB API tests
│   └── test_auth.py        # Auth tests
├── static/
│   ├── css/
│   │   └── style.css       # Dark theme styles
│   ├── js/
│   │   ├── app.js          # Main app logic
│   │   ├── search.js       # Game search
│   │   ├── review.js       # Review/rating logic
│   │   └── profile.js      # Profile page
│   └── img/
│       └── default-game.png # Placeholder
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Home/discover page
│   ├── game.html           # Game detail page
│   ├── profile.html        # User profile
│   ├── search.html         # Search results
│   └── lists.html          # Lists/shelves
└── docs/
    └── plans/
        └── gamevault-plan.md  # This file
```

---

## Phase 1: Foundation (Tasks 1-5)

### Task 1: Project Setup and Dependencies

**Objective:** Initialize the project with Flask, SQLAlchemy, and test infrastructure.

**Files:**
- Create: `~/gamevault/requirements.txt`
- Create: `~/gamevault/config.py`
- Create: `~/gamevault/app.py` (minimal Flask app)
- Create: `~/gamevault/tests/conftest.py`

**Step 1: Write requirements.txt**
```
flask==3.1.1
flask-sqlalchemy==3.1.1
requests==2.32.3
pytest==8.3.5
pytest-flask==1.3.0
```

**Step 2: Write config.py**
```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///gamevault.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IGDB_CLIENT_ID = os.environ.get('IGDB_CLIENT_ID', '')
    IGDB_CLIENT_SECRET = os.environ.get('IGDB_CLIENT_SECRET', '')
```

**Step 3: Write minimal app.py**
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    return app
```

**Step 4: Write conftest.py**
```python
import pytest
from app import create_app, db as _db

@pytest.fixture
def app():
    app = create_app('config.Config')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
```

**Step 5: Verify**
```bash
cd ~/gamevault && python -m pytest tests/ -v
```
Expected: Tests collection works (may have 0 tests, but no import errors)

---

### Task 2: Database Models

**Objective:** Define User, Game, Review, and List models with TDD.

**Files:**
- Create: `~/gamevault/models.py`
- Create: `~/gamevault/tests/test_models.py`

**Step 1: Write failing tests**
```python
# tests/test_models.py
from models import User, Game, Review, GameList

def test_user_creation():
    user = User(username='cassie', email='cassie@example.com')
    assert user.username == 'cassie'
    assert user.email == 'cassie@example.com'
    assert user.created_at is not None

def test_game_creation():
    game = Game(igdb_id=12345, name='Marathon', release_date='1994-12-21')
    assert game.igdb_id == 12345
    assert game.name == 'Marathon'

def test_review_creation():
    review = Review(rating=5, body='Amazing game')
    assert review.rating == 5
    assert review.body == 'Amazing game'
    assert review.created_at is not None

def test_review_rating_bounds():
    from sqlalchemy.exc import IntegrityError
    review = Review(rating=6)  # Should fail
    # Test that rating is clamped to 1-5
```

**Step 2: Run tests to verify failure**
```bash
cd ~/gamevault && python -m pytest tests/test_models.py -v
```
Expected: FAIL — ImportError (models not defined yet)

**Step 3: Implement models.py**
```python
from datetime import datetime, timezone
from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reviews = db.relationship('Review', backref='user', lazy=True)
    lists = db.relationship('GameList', backref='user', lazy=True)

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    igdb_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    release_date = db.Column(db.String(20))
    cover_url = db.Column(db.String(500))
    summary = db.Column(db.Text)
    genres = db.Column(db.String(200))
    platforms = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reviews = db.relationship('Review', backref='game', lazy=True)

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))

class GameList(db.Model):
    __tablename__ = 'game_lists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    games = db.relationship('Game', secondary='list_games')

list_games = db.Table('list_games',
    db.Column('list_id', db.Integer, db.ForeignKey('game_lists.id'), primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('games.id'), primary_key=True)
)
```

**Step 4: Run tests to verify pass**
```bash
cd ~/gamevault && python -m pytest tests/test_models.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
cd ~/gamevault && git add -A && git commit -m "feat: add database models for User, Game, Review, GameList"
```

---

### Task 3: IGDB API Client

**Objective:** Build a client for searching games via IGDB API with TDD.

**Files:**
- Create: `~/gamevault/igdb.py`
- Create: `~/gamevault/tests/test_igdb.py`

**Step 1: Write failing tests**
```python
# tests/test_igdb.py
from igdb import IGDBClient

def test_client_initialization():
    client = IGDBClient(client_id='test', client_secret='test')
    assert client.client_id == 'test'

def test_search_returns_list():
    # Mock the API response
    client = IGDBClient(client_id='test', client_secret='test')
    # Test that search returns a list of games
    # (Will need mocking for actual API calls)
```

**Step 2: Implement igdb.py**
```python
import requests
import time

class IGDBClient:
    BASE_URL = 'https://api.igdb.com/v4'
    AUTH_URL = 'https://id.twitch.tv/oauth2/token'
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
        self._token_expiry = 0
    
    def _get_access_token(self):
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token
        
        response = requests.post(self.AUTH_URL, params={
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        })
        response.raise_for_status()
        data = response.json()
        self._access_token = data['access_token']
        self._token_expiry = time.time() + data['expires_in'] - 60
        return self._access_token
    
    def search_games(self, query, limit=10):
        token = self._get_access_token()
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {token}'
        }
        data = f'fields id, name, first_release_date, cover.url, summary, genres.name, platforms.name; search "{query}"; limit {limit};'
        response = requests.post(f'{self.BASE_URL}/games', headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    
    def get_game(self, igdb_id):
        token = self._get_access_token()
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {token}'
        }
        data = f'fields id, name, first_release_date, cover.url, summary, genres.name, platforms.name; where id = {igdb_id};'
        response = requests.post(f'{self.BASE_URL}/games', headers=headers, data=data)
        response.raise_for_status()
        results = response.json()
        return results[0] if results else None
```

**Step 3: Run tests**
```bash
cd ~/gamevault && python -m pytest tests/test_igdb.py -v
```

**Step 4: Commit**
```bash
cd ~/gamevault && git add -A && git commit -m "feat: add IGDB API client for game search"
```

---

### Task 4: Authentication System

**Objective:** Implement simple session-based authentication with TDD.

**Files:**
- Create: `~/gamevault/auth.py`
- Create: `~/gamevault/tests/test_auth.py`

**Step 1: Write failing tests**
```python
# tests/test_auth.py
def test_login_page_renders(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_register_creates_user(client, app):
    response = client.post('/register', data={
        'username': 'cassie',
        'email': 'cassie@example.com',
        'password': 'securepass123'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_login_with_valid_credentials(client, app):
    # Register first
    client.post('/register', data={
        'username': 'cassie',
        'email': 'cassie@example.com',
        'password': 'securepass123'
    })
    # Then login
    response = client.post('/login', data={
        'username': 'cassie',
        'password': 'securepass123'
    }, follow_redirects=True)
    assert response.status_code == 200
```

**Step 2: Implement auth.py**
```python
from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from app import db

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def register_user(username, email, password):
    if User.query.filter_by(username=username).first():
        return None, 'Username already exists'
    if User.query.filter_by(email=email).first():
        return None, 'Email already registered'
    
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()
    return user, None

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None
```

**Step 3: Run tests**
```bash
cd ~/gamevault && python -m pytest tests/test_auth.py -v
```

**Step 4: Commit**
```bash
cd ~/gamevault && git add -A && git commit -m "feat: add session-based authentication"
```

---

### Task 5: Flask Routes and Templates

**Objective:** Wire up all routes and create the base HTML template with dark theme.

**Files:**
- Create: `~/gamevault/routes.py`
- Create: `~/gamevault/templates/base.html`
- Create: `~/gamevault/templates/index.html`
- Create: `~/gamevault/templates/login.html`
- Create: `~/gamevault/templates/game.html`
- Create: `~/gamevault/templates/profile.html`
- Create: `~/gamevault/templates/search.html`
- Create: `~/gamevault/static/css/style.css`
- Create: `~/gamevault/tests/test_routes.py`

**Step 1: Write failing tests**
```python
# tests/test_routes.py
def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_game_page(client):
    response = client.get('/game/12345')
    assert response.status_code in [200, 404]

def test_search_page(client):
    response = client.get('/search?q=marathon')
    assert response.status_code == 200
```

**Step 2: Implement routes.py**
```python
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from models import Game, Review, GameList, User
from igdb import IGDBClient
from auth import login_required, register_user, authenticate_user
from app import db, app
import os

main = Blueprint('main', __name__)

igdb = IGDBClient(
    client_id=os.environ.get('IGDB_CLIENT_ID', ''),
    client_secret=os.environ.get('IGDB_CLIENT_SECRET', '')
)

@main.route('/')
def index():
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(10).all()
    return render_template('index.html', reviews=recent_reviews)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = authenticate_user(request.form['username'], request.form['password'])
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.index'))
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user, error = register_user(
            request.form['username'],
            request.form['email'],
            request.form['password']
        )
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.index'))
    return render_template('login.html', register=True)

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

@main.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        games = igdb.search_games(query)
    else:
        games = []
    return render_template('search.html', games=games, query=query)

@main.route('/game/<int:igdb_id>')
def game_detail(igdb_id):
    game = Game.query.filter_by(igdb_id=igdb_id).first()
    if not game:
        igdb_game = igdb.get_game(igdb_id)
        if igdb_game:
            game = Game(
                igdb_id=igdb_game['id'],
                name=igdb_game['name'],
                release_date=str(igdb_game.get('first_release_date', '')),
                cover_url=igdb_game.get('cover', {}).get('url', ''),
                summary=igdb_game.get('summary', ''),
                genres=', '.join([g['name'] for g in igdb_game.get('genres', [])]),
                platforms=', '.join([p['name'] for p in igdb_game.get('platforms', [])])
            )
            db.session.add(game)
            db.session.commit()
    
    reviews = Review.query.filter_by(game_id=game.id).all() if game else []
    return render_template('game.html', game=game, reviews=reviews)

@main.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    reviews = Review.query.filter_by(user_id=user.id).order_by(Review.created_at.desc()).all()
    lists = GameList.query.filter_by(user_id=user.id).all()
    return render_template('profile.html', user=user, reviews=reviews, lists=lists)

app.register_blueprint(main)
```

**Step 3: Create base.html template**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}GameVault{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="logo">GameVault</a>
        <form action="/search" method="get" class="search-form">
            <input type="text" name="q" placeholder="Search games..." value="{{ request.args.get('q', '') }}">
        </form>
        <div class="nav-links">
            {% if session.get('user_id') %}
                <a href="/profile/{{ session.username }}">{{ session.username }}</a>
                <a href="/logout">Logout</a>
            {% else %}
                <a href="/login">Login</a>
            {% endif %}
        </div>
    </nav>
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

**Step 4: Create style.css (dark theme)**
```css
:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-card: #1a1a25;
    --text-primary: #e0d8d0;
    --text-secondary: #8a8a90;
    --accent-gold: #d4a574;
    --accent-lavender: #9b8ec4;
    --accent-rose: #c48b8b;
    --border: rgba(212, 165, 116, 0.1);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Georgia', serif;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.navbar {
    display: flex;
    align-items: center;
    padding: 1rem 2rem;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
}

.logo {
    font-size: 1.5rem;
    color: var(--accent-gold);
    text-decoration: none;
    font-weight: 300;
    letter-spacing: 0.1em;
}

.search-form {
    flex: 1;
    max-width: 400px;
    margin: 0 2rem;
}

.search-form input {
    width: 100%;
    padding: 0.5rem 1rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--text-primary);
    font-family: inherit;
}

.nav-links a {
    color: var(--text-secondary);
    text-decoration: none;
    margin-left: 1.5rem;
    transition: color 0.2s;
}

.nav-links a:hover {
    color: var(--accent-gold);
}

.game-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    transition: transform 0.2s;
}

.game-card:hover {
    transform: translateY(-2px);
}

.rating {
    color: var(--accent-gold);
    font-size: 1.2rem;
}

.btn {
    padding: 0.5rem 1.5rem;
    background: var(--accent-gold);
    color: var(--bg-primary);
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-family: inherit;
    transition: opacity 0.2s;
}

.btn:hover {
    opacity: 0.9;
}

.btn-secondary {
    background: transparent;
    border: 1px solid var(--accent-gold);
    color: var(--accent-gold);
}
```

**Step 5: Run tests**
```bash
cd ~/gamevault && python -m pytest tests/test_routes.py -v
```

**Step 6: Commit**
```bash
cd ~/gamevault && git add -A && git commit -m "feat: add Flask routes, templates, and dark theme CSS"
```

---

## Phase 2: Core Features (Tasks 6-10)

### Task 6: Game Search with Autocomplete

**Objective:** Implement real-time game search with autocomplete dropdown.

**Files:**
- Create: `~/gamevault/static/js/search.js`
- Modify: `~/gamevault/templates/search.html`

**Step 1: Write failing test**
```python
def test_api_search(client):
    response = client.get('/api/search?q=marathon')
    assert response.status_code == 200
    assert isinstance(response.json, list)
```

**Step 2: Implement search API endpoint**
```python
# In routes.py
@main.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    games = igdb.search_games(query, limit=5)
    return jsonify(games)
```

**Step 3: Implement search.js**
```javascript
// static/js/search.js
const searchInput = document.querySelector('.search-input');
const resultsDiv = document.querySelector('.search-results');
let debounceTimer;

searchInput?.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        fetch(`/api/search?q=${encodeURIComponent(e.target.value)}`)
            .then(res => res.json())
            .then(games => {
                resultsDiv.innerHTML = games.map(game => `
                    <a href="/game/${game.id}" class="search-result">
                        <img src="${game.cover?.url || '/static/img/default-game.png'}" alt="${game.name}">
                        <span>${game.name}</span>
                    </a>
                `).join('');
            });
    }, 300);
});
```

**Step 4: Run tests and commit**
```bash
cd ~/gamevault && python -m pytest tests/ -v && git add -A && git commit -m "feat: add game search with autocomplete"
```

---

### Task 7: Review and Rating System

**Objective:** Allow users to rate games (1-5 stars) and write reviews.

**Files:**
- Create: `~/gamevault/static/js/review.js`
- Modify: `~/gamevault/templates/game.html`
- Create: `~/gamevault/tests/test_reviews.py`

**Step 1: Write failing tests**
```python
def test_submit_review(client, app):
    # Login first
    client.post('/register', data={'username': 'test', 'email': 'test@test.com', 'password': 'pass123'})
    
    response = client.post('/api/reviews', json={
        'game_igdb_id': 12345,
        'rating': 5,
        'body': 'Amazing game!'
    })
    assert response.status_code == 201

def test_get_reviews(client):
    response = client.get('/api/reviews/12345')
    assert response.status_code == 200
```

**Step 2: Implement review API**
```python
@main.route('/api/reviews', methods=['POST'])
@login_required
def create_review():
    data = request.json
    game = Game.query.filter_by(igdb_id=data['game_igdb_id']).first()
    if not game:
        # Create game from IGDB
        igdb_game = igdb.get_game(data['game_igdb_id'])
        game = Game(igdb_id=igdb_game['id'], name=igdb_game['name'])
        db.session.add(game)
        db.session.commit()
    
    review = Review(
        user_id=session['user_id'],
        game_id=game.id,
        rating=min(5, max(1, data['rating'])),
        body=data.get('body', '')
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({'id': review.id}), 201

@main.route('/api/reviews/<int:igdb_id>')
def get_reviews(igdb_id):
    game = Game.query.filter_by(igdb_id=igdb_id).first()
    if not game:
        return jsonify([])
    reviews = Review.query.filter_by(game_id=game.id).all()
    return jsonify([{
        'id': r.id,
        'rating': r.rating,
        'body': r.body,
        'username': r.user.username,
        'created_at': r.created_at.isoformat()
    } for r in reviews])
```

**Step 3: Implement review.js**
```javascript
// static/js/review.js
const ratingStars = document.querySelectorAll('.star');
const reviewForm = document.querySelector('.review-form');

ratingStars.forEach((star, index) => {
    star.addEventListener('click', () => {
        ratingStars.forEach((s, i) => {
            s.classList.toggle('active', i <= index);
        });
        document.querySelector('#rating').value = index + 1;
    });
});

reviewForm?.addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(reviewForm);
    fetch('/api/reviews', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            game_igdb_id: formData.get('game_igdb_id'),
            rating: parseInt(formData.get('rating')),
            body: formData.get('body')
        })
    }).then(() => location.reload());
});
```

**Step 4: Run tests and commit**
```bash
cd ~/gamevault && python -m pytest tests/ -v && git add -A && git commit -m "feat: add review and rating system"
```

---

### Task 8: Lists and Shelves

**Objective:** Create custom game lists (like Letterboxd lists).

**Files:**
- Create: `~/gamevault/static/js/lists.js`
- Modify: `~/gamevault/templates/lists.html`
- Create: `~/gamevault/tests/test_lists.py`

**Step 1: Write failing tests**
```python
def test_create_list(client, app):
    client.post('/register', data={'username': 'test', 'email': 'test@test.com', 'password': 'pass123'})
    response = client.post('/api/lists', json={
        'name': 'FPS Classics',
        'description': 'Best first-person shooters'
    })
    assert response.status_code == 201

def test_add_game_to_list(client, app):
    # Create list and add game
    pass
```

**Step 2: Implement list API**
```python
@main.route('/api/lists', methods=['POST'])
@login_required
def create_list():
    data = request.json
    game_list = GameList(
        user_id=session['user_id'],
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(game_list)
    db.session.commit()
    return jsonify({'id': game_list.id}), 201

@main.route('/api/lists/<int:list_id>/games', methods=['POST'])
@login_required
def add_game_to_list(list_id):
    data = request.json
    game_list = GameList.query.get_or_404(list_id)
    game = Game.query.filter_by(igdb_id=data['game_igdb_id']).first()
    if game and game not in game_list.games:
        game_list.games.append(game)
        db.session.commit()
    return jsonify({'success': True})
```

**Step 3: Run tests and commit**
```bash
cd ~/gamevault && python -m pytest tests/ -v && git add -A && git commit -m "feat: add game lists and shelves"
```

---

### Task 9: Profile Page with Stats

**Objective:** Build a profile page showing user stats, recent activity, and lists.

**Files:**
- Modify: `~/gamevault/templates/profile.html`
- Create: `~/gamevault/static/js/profile.js`

**Step 1: Implement profile template**
```html
{% extends "base.html" %}
{% block title %}{{ user.username }} - GameVault{% endblock %}
{% block content %}
<div class="profile-header">
    <h1>{{ user.username }}</h1>
    <p class="member-since">Member since {{ user.created_at.strftime('%B %Y') }}</p>
</div>

<div class="profile-stats">
    <div class="stat">
        <span class="stat-num">{{ reviews|length }}</span>
        <span class="stat-label">Reviews</span>
    </div>
    <div class="stat">
        <span class="stat-num">{{ lists|length }}</span>
        <span class="stat-label">Lists</span>
    </div>
</div>

<div class="recent-reviews">
    <h2>Recent Reviews</h2>
    {% for review in reviews[:5] %}
    <div class="review-card">
        <a href="/game/{{ review.game.igdb_id }}">{{ review.game.name }}</a>
        <div class="rating">{{ '★' * review.rating }}{{ '☆' * (5 - review.rating) }}</div>
        <p>{{ review.body[:100] }}{% if review.body|length > 100 %}...{% endif %}</p>
    </div>
    {% endfor %}
</div>
{% endblock %}
```

**Step 2: Run tests and commit**
```bash
cd ~/gamevault && python -m pytest tests/ -v && git add -A && git commit -m "feat: add profile page with stats"
```

---

### Task 10: Home Page with Discover Feed

**Objective:** Build the home page with recent reviews, popular games, and featured lists.

**Files:**
- Modify: `~/gamevault/templates/index.html`

**Step 1: Implement index template**
```html
{% extends "base.html" %}
{% block title %}GameVault - Discover Games{% endblock %}
{% block content %}
<div class="hero">
    <h1>GameVault</h1>
    <p>Your personal game database. Rate, review, and catalog every game you play.</p>
</div>

<section class="recent-activity">
    <h2>Recent Reviews</h2>
    <div class="review-grid">
        {% for review in reviews %}
        <div class="review-card">
            <a href="/game/{{ review.game.igdb_id }}">
                <img src="{{ review.game.cover_url or '/static/img/default-game.png' }}" alt="{{ review.game.name }}">
            </a>
            <h3><a href="/game/{{ review.game.igdb_id }}">{{ review.game.name }}</a></h3>
            <div class="rating">{{ '★' * review.rating }}{{ '☆' * (5 - review.rating) }}</div>
            <p class="reviewer">by <a href="/profile/{{ review.user.username }}">{{ review.user.username }}</a></p>
        </div>
        {% endfor %}
    </div>
</section>
{% endblock %}
```

**Step 2: Run tests and commit**
```bash
cd ~/gamevault && python -m pytest tests/ -v && git add -A && git commit -m "feat: add home page with discover feed"
```

---

## Phase 3: Polish (Tasks 11-12)

### Task 11: Responsive Design and Mobile

**Objective:** Make the site fully responsive for mobile devices.

**Files:**
- Modify: `~/gamevault/static/css/style.css`

**Step 1: Add responsive styles**
```css
@media (max-width: 768px) {
    .navbar {
        flex-direction: column;
        gap: 1rem;
    }
    
    .search-form {
        max-width: 100%;
        margin: 0;
    }
    
    .game-grid {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    }
    
    .profile-stats {
        flex-direction: column;
    }
}
```

**Step 2: Commit**
```bash
cd ~/gamevault && git add -A && git commit -m "feat: add responsive design for mobile"
```

---

### Task 12: Deployment and Startup Script

**Objective:** Create a startup script and deploy to exe.dev.

**Files:**
- Create: `~/gamevault/start.sh`
- Create: `~/gamevault/README.md`

**Step 1: Create start.sh**
```bash
#!/bin/bash
cd ~/gamevault
source venv/bin/activate
export FLASK_APP=app.py
export FLASK_ENV=production
python -m flask run --host=0.0.0.0 --port=8891
```

**Step 2: Create README.md**
```markdown
# GameVault

A Letterboxd-style game database and review site.

## Features
- Search games via IGDB API
- Rate and review games (1-5 stars)
- Create custom lists and shelves
- Profile with stats and activity

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "from app import db; db.create_all()"
```

## Run
```bash
./start.sh
```

Access at: https://hermes-sera.exe.xyz:8891
```

**Step 3: Commit**
```bash
cd ~/gamevault && git add -A && git commit -m "feat: add deployment scripts and documentation"
```

---

## Parallelization Strategy

**Phase 1 (Foundation):** Sequential — each task builds on the previous
**Phase 2 (Features):** Parallelizable — Tasks 6-9 can run concurrently
**Phase 3 (Polish):** Sequential — depends on all features being complete

**Subagent Dispatch:**
- Tasks 1-5: Sequential, one at a time
- Tasks 6-9: Parallel (3 subagents)
- Tasks 10-12: Sequential

**Review Process:**
After each task:
1. Spec compliance review
2. Code quality review
3. Only proceed when both pass
