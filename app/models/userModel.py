from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from ..database import db
from ..models import Movie, Screening, Booking, BookingStatus, CinemaHallSeat, MovieStatus, ScreeningStatus
from typing import List, Union, Tuple
from sqlalchemy.orm.exc import NoResultFound
import bcrypt
from datetime import datetime
from flask import session
from sqlalchemy import extract, desc

class General:
    @classmethod
    def getAllMovies(cls) -> List[Movie]:
        try:
            return Movie.query.filter(Movie.status == 'ACTIVE').all()
        except NoResultFound:
            return []

    @classmethod
    def searchMovieTitle(cls, title: str) -> List[Movie]:
        try:
            return Movie.query.filter(Movie.title == title, Movie.status == 'ACTIVE').all()
        except NoResultFound:
            return []

    @classmethod
    def searchMovieLang(cls, lang: str) -> List[Movie]:
        try:
            return Movie.query.filter(Movie.language == lang, Movie.status == 'ACTIVE').all()
        except NoResultFound:
            return []

    @classmethod
    def searchMovieGenre(cls, genre: str) -> List[Movie]:
        try:
            return Movie.query.filter(Movie.genre == genre, Movie.status == 'ACTIVE').all()
        except NoResultFound:
            return []

    @classmethod
    def searchMovieYear(cls, rYear: int) -> List[Movie]:
        try:
            return Movie.query.filter(extract('year', Movie.releaseDate) == rYear, Movie.status == 'ACTIVE').all()
        except NoResultFound:
            return []


class Person(General):
    name = db.Column(db.String)
    address = db.Column(db.String(255))
    email = db.Column(db.String, unique=True)
    phone = db.Column(db.String)


class Guest(General):
    @staticmethod
    def register(username: str, password: str) -> Tuple[bool, str]:
        existingUser = User.query.filter_by(username=username).first()
        if existingUser:
            return False, "Username already exists."
        newUser = Customer(username=username)
        newUser.password = password
        try:
            db.session.add(newUser)
            db.session.commit()
            return True, "User registered successfully."
        except Exception as e:
            db.session.rollback()
            return False, str(e)
        

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
    def cancelBooking(booking: Booking) -> Tuple[bool, str]:
        existingBooking = Booking.getBookingById(booking.id)
        if not existingBooking:
            return False, "Booking does not exist."
        elif existingBooking.status == BookingStatus.CANCELLED:
            return False, "Booking already cancelled."
        elif existingBooking.status == BookingStatus.PENDING:
            existingBooking.status = BookingStatus.CANCELLED
            db.session.commit()
            return True, "Booking cancelled successfully."
        elif existingBooking.status == BookingStatus.CONFIRMED:
            existingBooking.status = BookingStatus.CANCELLED

            refundAmount = existingBooking.payment.discountedAmount
            
            from models import Refund
            Refund.createRefund(existingBooking.payment.id, refundAmount, "Booking Canceled")
            db.session.commit()
            return True, "Booking canccelled successfully and refund has been processed."
        else:
            return False, "Unvalid booking status."


class Admin(User):

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    @property
    def bookings(self):
        raise AttributeError("Admin does not have access to a bookings list.")

    def addMovie(self, newMovie: Movie) -> Tuple[bool, str]:
        existingMovie = Movie.query.filter(Movie.title == newMovie.title, Movie.releaseDate == newMovie.releaseDate).first()

        if not existingMovie:
            db.session.add(newMovie)
            db.session.commit()
            return True, "Movie added successfully."
        return False, "Movie has already been in the database"

    def addScreening(self, newScreening: Screening) -> Tuple[bool, str]:
        existingScreening = Screening.query.filter(Screening.screeningDate == newScreening.screeningDate, Screening.startTime == newScreening.startTime, Screening.hallId == newScreening.hallId).first()
        # even the screening is new, still need to check time crashing and location crashing
        if existingScreening:
            return False, "Screening already exists."
        else:
            futureActiveScreeningList = []
            for screening in Screening.query.all():
                if screening.isActiveScreening() and screening.isFutureScreening():
                    futureActiveScreeningList.append(screening)
            for screening in futureActiveScreeningList:
                if newScreening.screeningDate.date() == screening.screeningDate.date() and newScreening.hallId == screening.hallId and ((newScreening.startTime.time() > screening.startTime.time() and newScreening.startTime.time() < screening.endTime.time()) or (newScreening.endTime.time() > screening.startTime.time() and newScreening.endTime.time() < screening.endTime.time())):
                    return False, "Time crash."
            db.session.add(newScreening)
            movie = Movie.getMovieById(newScreening.movieId)
            if movie.status == MovieStatus.ACTIVE:
                movie.screenings.append(newScreening)
            db.session.commit()
            return True, "Screening added successfully."
        
    
    def cancelMovie(self, movie: Movie) -> Tuple[bool, str]:
        existingMovie = Movie.getMovieById(movie.id)
        if not existingMovie:
            return False, "Movie not found."
        elif existingMovie.status == MovieStatus.CANCELLED:
            return False, "Movie is already cancelled"
        else:
            movie.status = MovieStatus.CANCELLED

            for screening in movie.screenings:
                if screening and screening.isFutureScreening() and screening.isActiveScreening():
                    self.cancelScreening(screening)

            db.session.commit()
            return True, "Movie cancelled successfully."


    def cancelScreening(self, screening: Screening) -> Tuple[bool, str]:
        existingScreening = Screening.getScreeningById(screening.id)

        if not existingScreening:
            return False, "Screening not found"
        elif not screening.isActiveScreening():
            return False, "Screening is already cancelled"
        elif not screening.isFutureScreening():
            return False, "Screening already finished"
        else:
            screening.status = ScreeningStatus.CANCELLED

            for booking in screening.bookings:
                success = BookingMixin.cancelBooking(booking)

                if not success:
                    continue

                else:
                    if booking.user.type == "customer":
                        booking.sendNotification(action="canceled")

            db.session.commit()
            return True, "Screening and its bookings cancelled successfully."


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
    
    def cancelBooking(self, booking: Booking) -> Tuple[bool, str]:
        success, message = super().cancelBooking(booking)
        if success:
            booking.sendNotification(action="canceled")
        return success, message
    
    def getBookingList(self) -> List[Booking]:
        return Booking.query.filter_by(userId=self.id).order_by(desc(Booking.createdOn)).all()