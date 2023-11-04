from app import db, app
from models import *

def create_database():
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("Tables created successfully!")

if __name__ == "__main__":
    create_database()