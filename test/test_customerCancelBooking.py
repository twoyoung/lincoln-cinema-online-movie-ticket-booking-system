import pytest
from flask import url_for

def test_customer_cancel_booking(test_client, init_database):
    # Assuming there's a booking with id=1 that can be cancelled
    booking_id = 1
    user_id = 1  # Assuming the user making the cancellation has user_id=1

    response = test_client.post(url_for('booking.cancelBooking', userId=user_id, bookingId=booking_id))

    assert response.status_code == 200 

    from app.models import Booking
    cancelled_booking = Booking.query.get(booking_id)
    assert cancelled_booking is not None
    assert cancelled_booking.status == 'CANCELLED'  
