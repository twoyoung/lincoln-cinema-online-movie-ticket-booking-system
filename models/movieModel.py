from datetime import datetime, date
from sqlalchemy.orm import relationship, backref
from app import db
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

class ScreeningValidationMixin:
    def isActiveScreening(self) -> bool:
        if self.status == ScreeningStatus.ACTIVE:
            return True
        return False
    
    def isFutureScreening(self) -> bool:
        today = datetime.now()
        now = datetime.now()
        if self.screeningDate > today or (self.screeningDate == today and self.startTime > now):
            return True
        return False
    
class BookingListFilterMixin:
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

    def getScreenings(self) -> List["Screening"]:
        screeningsList = []
        for screening in self.screenings:
            if screening and screening.isActiveScreening() and screening.isFutureScreening():
                screeningsList.append(screening)
        return screeningsList
    
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
        movie =  Movie.query.get(movieId)

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

    @staticmethod
    def getBookingById(bookingId: int) -> "Booking":
        return Booking.query.get(bookingId)
    
    @staticmethod
    def getAllBookings() -> List["Booking"]:
        return Booking.query.order_by(desc(Booking.createdOn)).all()

    @staticmethod
    def getFilteredBookingList() -> List["Booking"]:
        return Booking.query.filter(Booking.status != BookingStatus.CANCELLED).all()
        
    def sendNotification(self, action: str = "booked") -> Union["Notification", None]:
        from models import User
        user = User.getUserById(self.userId)
        if user.type == 'customer':

            seatNumbers = ", ".join([seat.seatNumber for seat in self.seats])
            if action == "booked":
                message = f"#{self.id} Booking confirmed!\nMovie: {self.screening.movie.title}\nDate & Time: {self.screening.screeningDate.strftime('%d-%m-%Y')}, {self.screening.startTime.strftime('%I:%M %p')}\nVenue: { self.screening.hall.name }\nSeat(s): {seatNumbers}\nTotal Amount Paid: ${self.payment.discountedAmount}"
            elif action == 'canceled':
                message = f"#{self.id} Booking cancelled successfully!\nBooking ID: {self.id}\nMovie: {self.screening.movie.title}\nDate & Time: {self.screening.screeningDate.strftime('%d-%m-%Y')}, {self.screening.startTime.strftime('%I:%M %p')}\nVenue: { self.screening.hall.name }\nSeat(s): {seatNumbers}\nTotal Amount Paid: ${self.payment.discountedAmount}"
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

    def getSeatChart(self):
        allSeats = {seat.seatNumber: seat for seat in self.hall.seats}
        reservedSeats = {seat for booking in BookingListFilterMixin.filteredBooking(self.bookings) for seat in booking.seats}
        rows = sorted(set(seat.seatRow for seat in allSeats.values()))
        maxColumns = max([seat.seatColumn for seat in allSeats.values()])

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
    
    @staticmethod
    def getScreeningById(screeningId: int) -> "Screening":
        screening = Screening.query.get(screeningId)
        if screening and screening.isActiveScreening() and screening.isFutureScreening():
            return screening
        else:
            return None
    
# Define the Notification table (assuming from previous discussion)
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String, nullable=False)
    isRead = db.Column(db.Boolean, default=False)
    timestamp = db.Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def numberOfUnreadNotifications():
        return Notification.query.filter_by(isRead=False).count()
    
    @staticmethod
    def getNotificationById(notificationId: int) -> 'Notification':
        return Notification.query.get(notificationId)
    
    def markRead(self):
        self.isRead = True
        db.session.commit()


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
    
    @staticmethod
    def getSeatById(seatId: int) -> "CinemaHallSeat":
        return CinemaHallSeat.query.get(seatId)


