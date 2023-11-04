from flask import Flask
from .database import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinema.db'

    db.init_app(app)
    app.secret_key = 'your_secret_key_here'


    from .routes.routes import movie_bp, auth_bp
    app.register_blueprint(movie_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app