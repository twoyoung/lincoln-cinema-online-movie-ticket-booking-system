from unittest import mock
from unittest.mock import Mock, patch

def test_browse_movies_successful(test_client, init_database):
    # Mock the returned movies
    mock_movies = [Mock(id=1, title="Movie1", status="ACTIVE"), Mock(id=2, title="Movie2", status="ACTIVE")]

    with patch('models.userModel.General.getAllMovies', return_value=mock_movies):
        response = test_client.get('/movies')
        
        # Assert the successful response
        assert response.status_code == 200
        assert b"Movie1" in response.data
        assert b"Movie2" in response.data


def test_search_movies_by_title(test_client, init_database):
    mock_movies = [Mock(id=1, title="TestMovie", status="ACTIVE")]

    with patch('models.userModel.General.searchMovieTitle', return_value=mock_movies):
        response = test_client.get('/movies?title=TestMovie')
        
        assert response.status_code == 200
        assert b"TestMovie" in response.data


def test_search_movies_by_language(test_client, init_database):
    mock_movies = [Mock(id=1, title="TestMovie", status="ACTIVE", language="English")]

    with patch('models.userModel.General.searchMovieLang', return_value=mock_movies):
        response = test_client.get('/movies?language=English')
        
        assert response.status_code == 200
        assert b"TestMovie" in response.data

def test_search_movies_by_genre(test_client, init_database):
    mock_movies = [Mock(id=1, title="TestMovie", status="ACTIVE", genre="Action")]

    with patch('models.userModel.General.searchMovieGenre', return_value=mock_movies):
        response = test_client.get('/movies?genre=Action')
        
        assert response.status_code == 200
        assert b"TestMovie" in response.data

def test_search_movies_by_year(test_client, init_database):
    mock_movie = Mock(id=1, title="TestMovie", status="ACTIVE", releaseDate="2022-05-01")

    # Assuming you've setup a method to mock 'extract' function from SQLAlchemy to return the year of releaseDate
    with patch('models.userModel.General.searchMovieYear', return_value=[mock_movie]):
        response = test_client.get('/movies?year=2022')
        
        assert response.status_code == 200
        assert b"TestMovie" in response.data