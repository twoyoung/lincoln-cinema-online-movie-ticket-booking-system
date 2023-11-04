from flask import template_rendered
from contextlib import contextmanager
from unittest.mock import patch
from app import app
from models.movieModel import CinemaHall, CinemaHallSeat, Screening

@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

def test_view_seat_chart(test_client, init_database):
    # Use actual model instances for CinemaHall and CinemaHallSeat, but mock necessary methods and attributes
    mock_hall = CinemaHall(id=1)
    CinemaHallSeat.seatNumber = property(lambda self: self._seatNumber, lambda self, value: setattr(self, '_seatNumber', value))
    seat1 = CinemaHallSeat()
    seat1.seatNumber = 'A1'
    seat2 = CinemaHallSeat()
    seat2.seatNumber = 'A2'
    mock_hall.seats = [seat1, seat2]
    mock_screening = Screening(id=1, hall=mock_hall)

    mock_booking = []  # Empty bookings

    with patch.object(Screening, 'getActiveScreeningById', return_value=mock_screening), \
         patch.object(Screening, 'filteredBooking', return_value=mock_booking):
        with captured_templates(app) as templates:
            response = test_client.get("/book/1/seats")
            print(response.data)
            assert response.status_code == 302
            assert len(templates) == 0
            template, context = templates[0]
            assert template.name == "seatChart.html"

            # Verify the seat matrix
            seatMatrix = context['seatMatrix']
            assert len(seatMatrix) == 1
            assert len(seatMatrix[0]) == 2

            # Check the seat data
            assert seatMatrix[0][0]['seatNumber'] == 'A1'
            assert seatMatrix[0][0]['status'] == 'available'
            assert seatMatrix[0][1]['seatNumber'] == 'A2'
            assert seatMatrix[0][1]['status'] == 'available'

    # Test with an invalid screening ID (not existing)
    with patch.object(Screening, 'getActiveScreeningById', return_value=None):
        response = test_client.get("/book/999/seats")
        assert response.status_code == 404
        assert b"Screening not found" in response.data



