import pytest
from flask import url_for

# Assuming addMovie is a route in your Flask application
def test_add_movie(test_client, init_database):
    # Movie data to be added
    movie_data = {
        'title': 'New Movie',
        'language': 'English',
        'genre': 'Action',
        'releaseDate': '2023-01-01',
        'durationMins': 120,
        'country': 'USA',
        'description': 'A new action-packed movie.'
    }

    # Post request to add a new movie
    response = test_client.post(url_for('movies.addMovie'), data=movie_data)

    # Check if the response is successful
    assert response.status_code == 200  # Or 302 if you expect a redirect

    # Fetch the movie from the database and assert its presence
    # You will need to import your Movie model and query it to check if the movie is added
    from app.models.movieModel import Movie
    movie = Movie.query.filter_by(title='New Movie').first()
    assert movie is not None
    assert movie.title == 'New Movie'
    assert movie.language == 'English'
    
