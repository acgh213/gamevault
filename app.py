from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_class="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    # Register routes blueprint
    from routes import routes

    app.register_blueprint(routes)

    return app
