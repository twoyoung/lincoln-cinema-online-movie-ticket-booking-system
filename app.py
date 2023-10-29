from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinema.db'
db = SQLAlchemy(app)

app.secret_key = 'your_secret_key_here'