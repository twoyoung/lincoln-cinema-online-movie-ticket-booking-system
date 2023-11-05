import json
from app import db
from app.models import Movie, User, CinemaHall, CinemaHallSeat, Screening, Coupon
from datetime import datetime

from run import app

print("Starting script...")
# Populate the database from JSON file
def populateDatabaseFromJson(filename):
    if filename == 'db_data.json':
        with open(filename, 'r') as file:
            data = json.load(file)
            print('Loading file...')

            for movieData in data.get('movies', []):
                movie = Movie(
                    title = movieData['title'],
                    language = movieData['language'],
                    genre = movieData['genre'],
                    releaseDate = datetime.strptime(movieData['releaseDate'], '%Y-%m-%d'),
                    country = movieData['country'],
                    description = movieData['description'],
                    durationMins = movieData['durationMins']
                )
                db.session.add(movie)
                print('Adding a movie to database...')

            for userData in data.get('users', []):
                user = User(
                    username = userData['username'],
                    password = userData['password'],
                    type = userData['type']
                ) 
                db.session.add(user)
                print('Adding a user to database...')

            # Populate cinema halls
            for hallData in data.get('cinemaHalls', []):
                hall = CinemaHall(**hallData)
                db.session.add(hall)
                print("Adding a hall to database...")

            # Populate screenings
            for screeningData in data.get('screenings', []):
                movie = Movie.query.filter_by(id=screeningData['movieId']).first()
                hall = CinemaHall.query.filter_by(id=screeningData['hallId']).first()
                if movie and hall:
                    screening = Screening(
                        movieId=movie.id, 
                        hallId=hall.id, 
                        screeningDate = datetime.strptime(screeningData['screeningDate'], '%Y-%m-%d'),
                        startTime = datetime.strptime(screeningData['startTime'], '%Y-%m-%d %H:%M:%S'),
                        endTime=datetime.strptime(screeningData['endTime'], '%Y-%m-%d %H:%M:%S'),
                        status = screeningData['status']
                    )
                    db.session.add(screening)
                print("Adding a screening to database...")

            # Populate cinema hall seats
            for seatData in data.get('cinemaHallSeats', []):
                hall = CinemaHall.query.filter_by(id=seatData['hallId']).first()
                if hall:
                    seat = CinemaHallSeat(**seatData)
                    db.session.add(seat)
                print("Adding a seat to database...")

            # Populate coupons
            for couponData in data.get('coupons', []):
                coupon = Coupon(
                    code=couponData['code'],
                    expiryDate=datetime.strptime(couponData['expiryDate'], '%Y-%m-%d %H:%M:%S'),
                    discount=couponData['discount']
                )
                db.session.add(coupon)
                print("Adding a coupon to database...")

            db.session.commit()
            print('Finished adding data to database...')

            

            

if __name__ == '__main__':
    print('Starting...')
    with app.app_context():
        populateDatabaseFromJson('db_data.json')