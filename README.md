# GameVault

**A Letterboxd for games** — track, rate, and discover video games. GameVault is a web application that lets you build your personal game library, write reviews, rate titles, and explore what others are playing.

## Features

- **Game Library** — Browse and search a curated collection of games
- **Personal Ratings** — Rate games on a scale and keep track of your favorites
- **Reviews** — Write detailed reviews and read what others think
- **User Profiles** — Build your profile showing your collection and activity
- **Discovery** — Find new games through recommendations and community activity

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url> ~/gamevault
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

5. **Run tests (optional):**
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

The application is available at: **[https://hermes-sera.exe.xyz:8891](https://hermes-sera.exe.xyz:8891)**
