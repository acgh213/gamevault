from datetime import datetime

from app import db


list_games = db.Table(
    "list_games",
    db.Column("list_id", db.Integer, db.ForeignKey("game_list.id"), primary_key=True),
    db.Column("game_id", db.Integer, db.ForeignKey("game.id"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship("Review", backref="author", lazy="dynamic")
    game_lists = db.relationship("GameList", backref="owner", lazy="dynamic")

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return f"<User {self.username}>"


class Game(db.Model):
    __tablename__ = "game"

    id = db.Column(db.Integer, primary_key=True)
    igdb_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    release_date = db.Column(db.String(20), nullable=True)
    cover_url = db.Column(db.String(500), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    genres = db.Column(db.JSON, nullable=True)
    platforms = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship("Review", backref="game", lazy="dynamic")
    game_lists = db.relationship("GameList", secondary=list_games, back_populates="games")

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return f"<Game {self.name}>"


class Review(db.Model):
    __tablename__ = "review"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    body = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint("rating >= 1 AND rating <= 5", name="check_review_rating_range"),
    )

    @db.validates("rating")
    def validate_rating(self, key, value):
        if value is not None and (value < 1 or value > 5):
            raise ValueError("Rating must be between 1 and 5")
        return value

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return f"<Review {self.id} user={self.user_id} game={self.game_id} rating={self.rating}>"


class GameList(db.Model):
    __tablename__ = "game_list"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    games = db.relationship("Game", secondary=list_games, back_populates="game_lists")

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return f"<GameList {self.name}>"
