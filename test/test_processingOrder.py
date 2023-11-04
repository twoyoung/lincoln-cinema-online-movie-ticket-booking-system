import pytest
from unittest.mock import patch, MagicMock
from controllers import MovieController
from models import Booking, Payment, Screening, Seats

# A fixture for the Flask test client
@pytest.fixture
def client():
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# A fixture for the movie controller
@pytest.fixture
def movie_controller():
    controller = MovieController()
    return controller

# Mock fixtures for database models and external dependencies
@pytest.fixture
def mock_screening(mocker):
    mock = mocker.patch('movie_booking.models.Screening')
    mock.query.filter_by.return_value.first.return_value = MagicMock(Screening)
    return mock

@pytest.fixture
def mock_seats(mocker):
    mock = mocker.patch('movie_booking.models.Seats')
    mock.query.filter.return_value.all.return_value = [MagicMock(Seats) for _ in range(5)]  # Mock 5 seat objects
    return mock

@pytest.fixture
def mock_booking(mocker):
    return mocker.patch('movie_booking.models.Booking')

@pytest.fixture
def mock_payment_processor(mocker):
    return mocker.patch('movie_booking.controllers.payment_processor.PaymentProcessor')

# The actual test for processBooking
def test_process_booking(client, movie_controller, mock_screening, mock_seats, mock_booking, mock_payment_processor):
    user_id = 1
    screening_id = 1
    selected_seat_ids = ['A1', 'A2']
    payment_data = {'card_number': '1234-5678-1234-5678', 'expiry_date': '10/23', 'cvv': '123'}
    
    # Mock the payment processing to return successful transaction
    mock_payment_processor.process_payment.return_value = True

    # Call the processBooking function
    with patch.object(movie_controller, 'processBooking', return_value=True) as mock_process:
        result = movie_controller.processBooking(user_id, screening_id, selected_seat_ids, payment_data)

    # Assertions
    mock_screening.query.filter_by.assert_called_with(id=screening_id)
    mock_seats.query.filter.assert_called_with(Seats.id.in_(selected_seat_ids))
    mock_payment_processor.process_payment.assert_called_once_with(payment_data)
    mock_booking.assert_called_with(user_id=user_id, screening_id=screening_id, seats=selected_seat_ids, payment_confirmed=True)

    assert result is True
