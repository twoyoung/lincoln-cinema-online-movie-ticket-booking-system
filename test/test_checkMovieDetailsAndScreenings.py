import contextlib
from unittest.mock import Mock, patch


def test_view_movie_details_and_screenings_active_movie(test_client, init_database):
    mock_movie = Mock(
        id=1,
        title="TestMovie",
        status='models.movieModel.MovieStatus.ACTIVE',
    )
    mock_screening1 = "models.movieModel.Screening(id=1, screeningDate=datetime.datetime.now())"
    mock_screening2 = "models.movieModel.Screening(id=2, screeningDate=datetime.datetime.now())"
    mock_movie.screenings = [mock_screening1, mock_screening2]
    
    with patch('models.movieModel.Movie.getActiveMovieById', return_value=mock_movie):
        response = test_client.get('/movies/1')
        
        assert response.status_code == 200
        assert b"TestMovie" in response.data

        # Checking the movie's screening list.
        screenings_from_context = contextlib.get('screeningsByDate')
        expected_dates = [mock_screening1.screeningDate.date(), mock_screening2.screeningDate.date()]
        assert set(screenings_from_context.keys()) == set(expected_dates)
        for date, screenings in screenings_from_context.items():
            assert date in expected_dates
            for screening in screenings:
                assert screening in [mock_screening1, mock_screening2]


def test_view_movie_details_and_screenings_inactive_movie(test_client, init_database):
    with patch('models.movieModel.Movie.getActiveMovieById', return_value=None):
        response = test_client.get('/movies/1')
        
        assert response.status_code == 302  # Since we are redirecting
        # Now, check if the flash message is as expected
        with test_client.session_transaction() as session:
            flash_messages = dict(session['_flashes'])
            assert 'error' in flash_messages
            assert flash_messages['error'] == 'Movie does not exist or has been cancelled.'
            session.clear()


