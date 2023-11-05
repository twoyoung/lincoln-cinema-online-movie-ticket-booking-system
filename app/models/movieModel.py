from datetime import datetime, date
from sqlalchemy.orm import relationship, backref
from ..database import db
from typing import List, Union
from enum import Enum
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import DateTime, desc

class MovieStatus(Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"

class ScreeningStatus(Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    FINISHED = "FINISHED"

class BookingStatus(Enum):
    PENDING = 1
    CONFIRMED = 2
    CANCELLED = 3

# an abstract mixin class to check if a screening is status active and start time in the future
class ScreeningValidationMixin:

    # method to check if the screening's status is active
    def isActiveScreening(self) -> bool:
        if self.status == ScreeningStatus.ACTIVE:
            return True
        return False
    
    # method to check if the screening is in the future
    def isFutureScreening(self) -> bool:
        today = datetime.now()
        now = datetime.now()
        if self.screeningDate.date() > today.date() or (self.screeningDate.date() == today.date() and self.startTime.time() > now.time()):
            return True
        return False
    
# a mixin class to filter the booking list
class BookingListFilterMixin:

    # method to filter the booking list to get rid of canceled bookings
    @staticmethod
    def filteredBooking(bookingList: ["Booking"]) -> ["Booking"]:
        filteredBookingList = []
        for booking in bookingList:
            if booking.status == BookingStatus.PENDING or booking.status == BookingStatus.CONFIRMED:
                filteredBookingList.append(booking)
        return filteredBookingList


# Define the Movie table
class Movie(db.Model, ScreeningValidationMixin):
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

    # method to get the movie's screenings list
    def getScreenings(self) -> List["Screening"]:
        screeningsList = []
        for screening in self.screenings:
            if screening and screening.isActiveScreening() and screening.isFutureScreening():
                screeningsList.append(screening)
        return screeningsList
    
    # method to add a screening to the movie
    def addScreening(self, screening) -> bool:
        if screening not in self.screenings:
            self.screenings.append(screening)
            db.session.add(screening)
            db.session.commit()
            return True
        return False

    # method to remove a screening from the movie's screening list
    def removeScreening(self, screening) -> bool:
        if screening in self.screenings:
            self.screenings.remove(screening)
            return True
        return False
    
    # method to get the movie by id
    @staticmethod
    def getMovieById(movieId: int) -> Union["Movie", None]:
        return  Movie.query.get(movieId)

    # method to only get active movie by id
    @staticmethod
    def getActiveMovieById(movieId: int) -> Union["Movie", None]:
        movie = Movie.query.get(movieId)
        if movie and movie.status == MovieStatus.ACTIVE:
            return movie
        else:
            return None

# Define the Booking table
class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship('User', back_populates='bookings')
    numberOfSeats = db.Column(db.Integer, nullable=False)
    createdOn = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(BookingStatus), nullable=False)
    screeningId = db.Column(db.Integer, db.ForeignKey('screenings.id'))
    screening = relationship('Screening', back_populates='bookings')
    orderTotal = db.Column(db.Float, nullable=False)
    paymentId = db.Column(db.Integer, db.ForeignKey('payments.id'))
    payment = relationship('Payment', back_populates='booking', uselist=False)

    seats = relationship('CinemaHallSeat', backref='bookings')

    # method to get the booking by id
    @staticmethod
    def getBookingById(bookingId: int) -> Union["Booking", None]:
        return Booking.query.get(bookingId)
    
    # method to get all bookings in database
    @staticmethod
    def getAllBookings() -> List["Booking"]:
        return Booking.query.order_by(desc(Booking.createdOn)).all() # ordered from the newest booking to the oldest booking

    # method to get all active bookings
    @staticmethod
    def getFilteredBookingList() -> List["Booking"]:
        return Booking.query.filter(Booking.status != BookingStatus.CANCELLED).all()

    # method to send notification 
    def sendNotification(self, action: str = "booked") -> Union["Notification", None]:
        from .userModel import User
        user = User.getUserById(self.userId)

        # only send notifications to registered customers
        if user.type == 'customer':

            seatNumbers = ", ".join([seat.seatNumber for seat in self.seats])
            if action == "booked":
                message = f"#{self.id} Booking confirmed!\nMovie: {self.screening.movie.title}\nDate & Time: {self.screening.screeningDate.strftime('%d-%m-%Y')}, {self.screening.startTime.strftime('%I:%M %p')}\nVenue: { self.screening.hall.name }\nSeat(s): {seatNumbers}"
            elif action == 'canceled':
                message = f"#{self.id} Booking cancelled!\nBooking ID: {self.id}\nMovie: {self.screening.movie.title}\nDate & Time: {self.screening.screeningDate.strftime('%d-%m-%Y')}, {self.screening.startTime.strftime('%I:%M %p')}\nVenue: { self.screening.hall.name }\nSeat(s): {seatNumbers}"
            else:
                raise ValueError("Invalid action for notification")
            
            notification = Notification(
                userId = self.userId,
                message = message
            )
        
            user.notifications.append(notification)
            db.session.add(notification)
            db.session.commit()

            return notification


# Screening class/table
class Screening(db.Model, ScreeningValidationMixin, BookingListFilterMixin):
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

    # method to get the screening's seat chart
    def getSeatChart(self):
        allSeats = {seat.seatNumber: seat for seat in self.hall.seats}

        # according to the bookings, get the reserved seats list
        reservedSeats = {seat for booking in BookingListFilterMixin.filteredBooking(self.bookings) for seat in booking.seats}
        rows = sorted(set(seat.seatRow for seat in allSeats.values()))
        maxColumns = max([seat.seatColumn for seat in allSeats.values()])

        # restructure the seats to be two dimentional to fit for rendering in html
        seatMatrix = []
        for row in rows:
            seatRow = []
            for col in range(1, maxColumns + 1):
                seatNumber = f"{row}{col}"
                seat = allSeats.get(seatNumber)
                if seat:
                    status = 'reserved' if seat in reservedSeats else 'available'
                    seatRow.append({'seatNumber': seatNumber, 'status': status, 'seatObject': seat})
                else:
                    seatRow.append(None)
            seatMatrix.append(seatRow)
        return seatMatrix
    
    # method to get active screening by id
    @staticmethod
    def getActiveScreeningById(screeningId: int) -> Union["Screening", None]:
        screening = Screening.query.get(screeningId)
        if screening and screening.isActiveScreening() and screening.isFutureScreening():
            return screening
        else:
            return None
        
    # method to get any screening by id
    @staticmethod
    def getScreeningById(screeningId: int) -> Union["Screening", None]:
        return Screening.query.get(screeningId)
    
# Define the Notification table
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String, nullable=False)
    isRead = db.Column(db.Boolean, default=False)
    timestamp = db.Column(DateTime, default=datetime.utcnow)

    # method to get the number of unread notifications
    @staticmethod
    def numberOfUnreadNotifications():
        return Notification.query.filter_by(isRead=False).count()
    
    # method to get notification by id
    @staticmethod
    def getNotificationById(notificationId: int) -> 'Notification':
        return Notification.query.get(notificationId)
    
    # method to mark the notification as read
    def markRead(self):
        self.isRead = True
        db.session.commit()

# CinemaHall class/table
class CinemaHall(db.Model):
    __tablename__ = 'cinemaHalls'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    totalSeats = db.Column(db.Integer, nullable=False)
    
    seats = relationship('CinemaHallSeat', back_populates='hall')
    screenings = relationship('Screening', back_populates='hall')

# CinemaHallSeat class/table
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

    # method to get seat number (row number + column number)
    @property
    def seatNumber(self):
        return f"{self.seatRow}{self.seatColumn}"
    
    # method to get the seat by id
    @staticmethod
    def getSeatById(seatId: int) -> "CinemaHallSeat":
        return CinemaHallSeat.query.get(seatId)


