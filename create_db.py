from app import create_app
from app.database import db
from app.models import *

def create_database():
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("Tables created successfully!")

if __name__ == "__main__":
    app = create_app()
    create_database()