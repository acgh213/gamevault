# GameVault

**A Letterboxd for games** — track, rate, and discover video games. GameVault is a Flask web application that lets you build your personal game library, write reviews, rate titles, and explore what others are playing. Powered by the IGDB API for rich game data.

## Features

- **Game Library** — Browse and search a curated collection of games with cover art and metadata from IGDB
- **Personal Ratings** — Rate games on a 1–10 scale and keep track of your favorites
- **Reviews** — Write detailed reviews and read what the community thinks
- **User Profiles** — Build your profile showing your collection, ratings, and review activity
- **Discovery** — Find new games through recommendations and community activity
- **Authentication** — Secure user login and session management
- **92+ Tests** — Comprehensive test suite covering routes, models, and API interactions

## Screenshots

<!-- TODO: Add screenshots of the app -->

| Home Page | Game Detail | User Profile |
|-----------|-------------|--------------|
| ![Screenshot](https://via.placeholder.com/400x250?text=GameVault+Home) | ![Screenshot](https://via.placeholder.com/400x250?text=Game+Detail) | ![Screenshot](https://via.placeholder.com/400x250?text=Profile) |

## Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript (Jinja2 templates)
- **API Integration:** IGDB API (Twitch OAuth)
- **Testing:** pytest, pytest-flask, responses
- **Deployment:** Gunicorn/Werkzeug on Linux

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/acgh213/gamevault.git ~/gamevault
   cd ~/gamevault
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
   python -c "from app import db; db.create_all()"
   ```

5. **(Optional) Configure IGDB API credentials** in `config.py` or environment variables:
   ```bash
   export IGDB_CLIENT_ID="your_client_id"
   export IGDB_CLIENT_SECRET="your_client_secret"
   ```

6. **Run tests (optional):**
   ```bash
   python -m pytest
   ```

## Run

**Production:**
```bash
./start.sh
```

**Development:**
```bash
cd ~/gamevault
source venv/bin/activate
export FLASK_APP=app.py
export FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=8891
```

## Access

The application is deployed at: **[https://hermes-sera.exe.xyz:8891](https://hermes-sera.exe.xyz:8891)**

## GitHub

[https://github.com/acgh213/gamevault](https://github.com/acgh213/gamevault)

## License

MIT
