import json
from app import app, db
from models import Movie, User, CinemaHall, CinemaHallSeat, Screening
from datetime import datetime

print("Starting script...")
# Populate the database from JSON file
def populateDatabaseFromJson(filename):
    if filename == 'movies.json':
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
                movie = Movie.query.filter_by(title=screeningData['title']).first()
                hall = CinemaHall.query.filter_by(name=screeningData['hallName']).first()
                if movie and hall:
                    screening = Screening(movieId=movie.id, hallId=hall.id, **screeningData)
                    db.session.add(screening)
                print("Adding a screening to database...")

            # Populate cinema hall seats
            for seatData in data.get('cinemaHallSeats', []):
                hall = CinemaHall.query.filter_by(name=seatData['hallName']).first()
                if hall:
                    seat = CinemaHallSeat(**seatData, hallId=hall.id)
                    db.session.add(seat)
                print("Adding a seat to database...")

            db.session.commit()
            print('Finished adding data to database...')

            

            

if __name__ == '__main__':
    print('Starting...')
    with app.app_context():
        populateDatabaseFromJson('movies.json')