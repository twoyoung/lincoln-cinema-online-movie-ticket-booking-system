from sqlalchemy.orm import relationship, backref
from app import db
from typing import List
from enum import Enum
from sqlalchemy.orm.exc import NoResultFound

class MovieStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"

class ScreeningStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    FINISHED = "finished"

class BookingStatus(Enum):
    PENDING = 1
    CONFIRMED = 2
    CANCELLED = 3

# Define the Movie table
class Movie(db.Model):
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    language = db.Column(db.String)
    genre = db.Column(db.String)
    releaseDate = db.Column(db.DateTime)
    durationMins = db.Column(db.Integer)
    country = db.Column(db.String)
    description = db.Column(db.String)
    status = db.Column(db.Enum(MovieStatus), nullable=False, default=MovieStatus.ACTIVE)
    # ratings
    # posterImage

    screenings = relationship("Screening", backref="movies")

    def getScreenings(self) -> List["Screening"]:
        return self.screenings
    
    def addScreening(self, screening) -> bool:
        if screening not in self.screenings:
            self.screenings.append(screening)
            db.session.add(screening)
            db.session.commit()
            return True
        return False

    def removeScreening(self, screening) -> bool:
        if screening in self.screenings:
            self.screenings.remove(screening)
            return True
        return False
    
    @staticmethod
    def getMovieById(movieId: int) -> "Movie":
        return Movie.query.get(movieId)

# Define the Booking table
class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship('Customer', back_populates='bookings')
    numberOfSeats = db.Column(db.Integer, nullable=False)
    createdOn = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(BookingStatus), nullable=False)
    screeningId = db.Column(db.Integer, db.ForeignKey('screenings.id'))
    screening = relationship('Screening', back_populates='bookings')
    orderTotal = db.Column(db.Float, nullable=False)
    paymentId = db.Column(db.Integer, db.ForeignKey('payments.id'))
    payment = relationship('Payment', back_populates='booking', uselist=False)

    seats = relationship('CinemaHallSeat', backref='bookings')

    @staticmethod
    def getBookingById(bookingId: int) -> "Booking":
        return Booking.query.get(bookingId)
    
    @staticmethod
    def getBookingList(self) -> List["Booking"]:
        return Booking.query.filter(Booking.status != BookingStatus.CANCELLED).all()
        
    def sendNotification(self, action: str = "booked") -> "Notification":
        seatNumbers = ", ".join([seat.seatNumber for seat in self.seats])
        if action == "booked":
            message = f"Your booking with ID {self.id} for movie {self.screening.movie.title} on {self.screening.screeningDate} {self.screening.startTime} at seat {seatNumbers} is confirmed. "
        elif action == 'canceled':
            message = f"Your booking with ID {self.id} for movie {self.screening.movie.title} on {self.screening.screeningDate} {self.screening.startTime} at seat {seatNumbers} has been successfully canceled. "
        else:
            raise ValueError("Invalid action for notification")
        
        notification = Notification(
            userId = self.userId,
            message = message
        )
        user = "User".getUserById(self.userId)
        if user.type == 'customer':
            user.notifications.append(notification)
            db.session.add(notification)
            db.session.commit()



class Screening(db.Model):
    __tablename__ = 'screenings'
    
    id = db.Column(db.Integer, primary_key=True)
    screeningDate = db.Column(db.DateTime, nullable=False)
    startTime = db.Column(db.DateTime, nullable=False)
    endTime = db.Column(db.DateTime, nullable=False)
    hallId = db.Column(db.Integer, db.ForeignKey('cinemaHalls.id'))
    status = db.Column(db.Enum(ScreeningStatus), nullable=False, default=ScreeningStatus.ACTIVE)
    
    
    movieId = db.Column(db.Integer, db.ForeignKey('movies.id'))
    movie = relationship('Movie', back_populates='screenings')
    hall = relationship('CinemaHall', back_populates='screenings')
    bookings = relationship('Booking', back_populates='screening')

    def getSeatChart(self):
        allSeats = set(self.hall.seats)
        reservedSeats = {seat for booking in self.bookings for seat in booking.seats}
        # for booking in self.bookings:
        #     for seat in booking.seats:
        #         reservedSeats.append(seat)
        availableSeats = allSeats - reservedSeats
        seatChart = {
            'available': list(availableSeats),
            'reserved': list(reservedSeats)
        }
        return seatChart
    
    @staticmethod
    def getScreeningById(screeningId: int) -> "Screening":
        try:
            return Screening.query.get(screeningId)
        except NoResultFound:
            return None
    
# Define the Notification table (assuming from previous discussion)
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String, nullable=False)

class CinemaHall(db.Model):
    __tablename__ = 'cinemaHalls'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    totalSeats = db.Column(db.Integer, nullable=False)
    
    seats = relationship('CinemaHallSeat', back_populates='hall')
    screenings = relationship('Screening', back_populates='hall')

class CinemaHallSeat(db.Model):
    __tablename__ = 'cinemaHallSeats'
    
    id = db.Column(db.Integer, primary_key=True)
    seatRow = db.Column(db.String, nullable=False)
    seatColumn = db.Column(db.Integer, nullable=False)
    seatType = db.Column(db.String, nullable=False)
    seatPrice = db.Column(db.Float, nullable=False)
    hallId = db.Column(db.Integer, db.ForeignKey('cinemaHalls.id'))
    bookingId = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    hall = relationship('CinemaHall', back_populates='seats')

    @property
    def seatNumber(self):
        return f"{self.seatRow}{self.seatColumn}"



