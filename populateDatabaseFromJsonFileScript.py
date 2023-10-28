import json
from app import db


# Populate the database from JSON file
def populateDatabaseFromJson(filename):

    if filename == 'movies':
        with open(filename, 'r') as file:
            data = json.load(file)

            for movieData in data.get('movies', []):
                movie = Movie(
                    title = movieData['title'],
                    language = movieData['language'],
                    genre = movieData['genre'],
                    releaseDate = movieData['releaseDate'],
                    country = movieData['country'],
                    description = movieData['description'],
                    durationMins = movieData['durationMins']
                )
                db.session.add(movie)

            for userData in data.get('users', []):
                user = User(
                    username = userData['username'],
                    password = userData['password'],
                    userType = userData['userType']
                ) 
                db.session.add(user)

            db.session.commit()

if __name__ == '__main__':
    populateDatabaseFromJson('movies.json')