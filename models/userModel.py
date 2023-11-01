from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from app import db
from models import Movie, Screening, Booking, BookingStatus, CinemaHallSeat, MovieStatus, ScreeningStatus
from typing import List, Union, Tuple
from sqlalchemy.orm.exc import NoResultFound
import bcrypt
from datetime import datetime
from flask import session
from sqlalchemy import extract

class General:
    @classmethod
    def getAllMovies(cls) -> List[Movie]:
        try:
            return Movie.query.all()
        except NoResultFound:
            return []

    @classmethod
    def searchMovieTitle(cls, title: str) -> List[Movie]:
        try:
            return Movie.query.filter(Movie.title == title).all()
        except NoResultFound:
            return []

    @classmethod
    def searchMovieLang(cls, lang: str) -> List[Movie]:
        try:
            return Movie.query.filter(Movie.language == lang).all()
        except NoResultFound:
            return []

    @classmethod
    def searchMovieGenre(cls, genre: str) -> List[Movie]:
        try:
            return Movie.query.filter(Movie.genre == genre).all()
        except NoResultFound:
            return []

    @classmethod
    def searchMovieYear(cls, rYear: int) -> List[Movie]:
        try:
            return Movie.query.filter(extract('year', Movie.releaseDate) == rYear).all()
        except NoResultFound:
            return []


class Person(General):
    name = db.Column(db.String)
    address = db.Column(db.String(255))
    email = db.Column(db.String, unique=True)
    phone = db.Column(db.String)


class Guest(General):
    @staticmethod
    def register(username: str, password: str) -> bool:
        existingUser = User.query.filter_by(username=username).first()
        if existingUser:
            return False
        newUser = Customer(username, password)
        try:
            db.session.add(newUser)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return False
        

# Define the User table
class User(Person, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255)) # discriminator field
    username = db.Column(db.String, unique=True, nullable=False)
    _password = db.Column(db.String, nullable=False)

    bookings = db.relationship("Booking", back_populates='user')
    
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def login(username: str, password: str) -> Tuple[bool, str]:
        user = User.query.filter_by(username=username).first()
        if not user:
            return False, "Username not found."
        
        if bcrypt.checkpw(password.encode('utf-8'), user._password.encode('utf-8')):
            session['userId'] = user.id
            session['userType'] = user.type
            return True, "Logged in successfully."
        else:
            return False, "Incorrect password."

    @staticmethod
    def logout() -> Tuple[bool, str]:
        if 'userId' not in session:
            return False, "Already logged out or session not started."
        session.pop('userId', None)
        session.pop('userType', None)
        return True, "Logged out successfully."
    
    def resetPassword(self, newPassword: str) -> bool:
        self.password = newPassword
        return True
    
    @staticmethod
    def getUserById(userId: int) -> Union["FrontDeskStaff", "Customer", "Admin", "User"]:
        return User.query.get(userId)

class BookingMixin:
    def makeBooking(self, booking: Booking) -> bool:
        seatIds = [seat.id for seat in booking.seats]
        existingBooking = Booking.query.join(Booking.seats).filter(Booking.screeningId == booking.screeningId, 
                       Booking.status != BookingStatus.CANCELLED, CinemaHallSeat.id.in_(seatIds)).first()
        if not existingBooking:
            db.session.add(booking)
            db.session.commit()
            return True
        return False

    @staticmethod
    def cancelBooking(booking: Booking) -> bool:
        existingBooking = Booking.query.get(booking.id)
        if existingBooking.status == BookingStatus.CANCELLED:
            return False
        elif existingBooking and existingBooking.status == BookingStatus.PENDING:
            existingBooking.status = BookingStatus.CANCELLED
            db.session.commit()
        elif existingBooking and existingBooking.status == BookingStatus.CONFIRMED:
            existingBooking.status = BookingStatus.CANCELLED

            refundAmount = existingBooking.payment.discountedAmount

            "Refund".createRefund(existingBooking.payment.id, refundAmount, "Booking Canceled")
            db.session.commit()
            return True
        else:
            return False


class Admin(User):

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    @property
    def bookings(self):
        raise AttributeError("Admin does not have access to a bookings list.")

    def addMovie(self, newMovie: Movie) -> bool:
        existingMovie = Movie.query.filter_by(Movie.title == newMovie.title, Movie.releaseDate == newMovie.releaseDate).first()

        if not existingMovie:
            db.session.add(newMovie)
            db.session.commit()
            return True
        return False

    def addScreening(self, newScreening: Screening) -> bool:
        existingScreening = Screening.query.filter_by(Screening.screeningDate == newScreening.screeningDate, Screening.startTime == newScreening.startTime, Screening.hallId == newScreening.hallId).first()

        if not existingScreening:
            db.session.add(newScreening)
            movie = Movie.getMovieById(newScreening.movieId)
            movie.screenings.append(newScreening)
            db.session.commit()
            return True
        return False
    
    def cancelMovie(self, movie: Movie):
        existingMovie = Movie.getMovieById(movie.id)
        if not existingMovie:
            return "Movie not found"
        elif existingMovie.status == MovieStatus.CANCELLED.value:
            return "Movie is already cancelled"
        else:
            movie.status = MovieStatus.CANCELLED.value

            currentDate = datetime.now().date()
            currentTime = datetime.now().time()
            for screening in movie.screenings:
                if screening.screeningDate > currentDate or (screening.screeningDate == currentDate and screening.startTime > currentTime):
                    self.cancelScreening(screening)

            db.session.commit()
            return "Movie and its future screenings cancelled successfully"


    def cancelScreening(self, screening: Screening):
        existingScreening = Screening.getScreeningById(screening.id)
        currentDate = datetime.now().date()
        currentTime = datetime.now().time()
        if not existingScreening:
            return "Screening not found"
        elif existingScreening.status == ScreeningStatus.CANCELLED.value:
            return "Screening is already cancelled"
        elif screening.screeningDate < currentDate or (screening.screeningDate == currentDate and screening.endTime < currentTime):
            return "Screening is already finished"
        else:
            screening.status = ScreeningStatus.CANCELLED.value

            for booking in screening.bookings:
                success = BookingMixin.cancelBooking(booking)

                if not success:
                    continue

                else:
                    if booking.user.type == "customer":
                        booking.sendNotification(action="canceled")

            db.session.commit()
            return "Screening and its bookings cancelled successfully."


class FrontDeskStaff(User, BookingMixin):

    __mapper_args__ = {
        'polymorphic_identity': 'staff',
    }


class Customer(User, BookingMixin):
    notifications = db.relationship("Notification", backref='users')

    __mapper_args__ = {
        'polymorphic_identity': 'customer',
    }

    def makeBooking(self, booking: Booking) -> bool:
        success = super().makeBooking(booking)
        if success:
            self.bookings.append(booking)
            db.session.commit()
        return success
    
    def cancelBooking(self, booking: Booking) -> bool:
        success = super().cancelBooking(booking)
        if success:
            booking.sendNotification(action="canceled")
        return success
    
    def getBookingList(self) -> List[Booking]:
        return self.bookings
