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

# General class
class General:

    # method to get all movies
    @classmethod
    def getAllMovies(cls) -> List[Movie]:
        try:
            return Movie.query.filter(Movie.status == 'ACTIVE').all()
        except NoResultFound:
            return []

    # method to search movies by title
    @classmethod
    def searchMovieTitle(cls, title: str) -> List[Movie]:
        try:
            return Movie.query.filter(Movie.title == title, Movie.status == 'ACTIVE').all()
        except NoResultFound:
            return []

    # method to search movies by language
    @classmethod
    def searchMovieLang(cls, lang: str) -> List[Movie]:
        try:
            return Movie.query.filter(Movie.language == lang, Movie.status == 'ACTIVE').all()
        except NoResultFound:
            return []

    # method to search movies by genre
    @classmethod
    def searchMovieGenre(cls, genre: str) -> List[Movie]:
        try:
            return Movie.query.filter(Movie.genre == genre, Movie.status == 'ACTIVE').all()
        except NoResultFound:
            return []

    # method to search movies by year
    @classmethod
    def searchMovieYear(cls, rYear: int) -> List[Movie]:
        try:
            return Movie.query.filter(extract('year', Movie.releaseDate) == rYear, Movie.status == 'ACTIVE').all()
        except NoResultFound:
            return []

# Person class
class Person(General):
    name = db.Column(db.String)
    address = db.Column(db.String(255))
    email = db.Column(db.String, unique=True)
    phone = db.Column(db.String)

# Guest class
class Guest(General):

    # method to register a new customer
    @staticmethod
    def register(username: str, password: str) -> Tuple[bool, str]:
        # check if the username is already registered
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

    # method to login
    @staticmethod
    def login(username: str, password: str) -> Tuple[bool, str]:

        # check if username exists
        user = User.query.filter_by(username=username).first()
        if not user:
            return False, "Username not found."
        
        # check if password correct
        if bcrypt.checkpw(password.encode('utf-8'), user._password.encode('utf-8')):
            session['userId'] = user.id
            session['userType'] = user.type
            return True, f"Welcome {username}! You have logged in successfully."
        else:
            return False, "Incorrect password."

    # method to logout
    @staticmethod
    def logout() -> Tuple[bool, str]:
        if 'userId' not in session:
            return False, "Already logged out or session not started."
        session.pop('userId', None)
        session.pop('userType', None)
        return True, "Logged out successfully."
    
    # method to reset password
    def resetPassword(self, newPassword: str) -> bool:
        self.password = newPassword
        return True
    
    # method to get the user by user ID
    @staticmethod
    def getUserById(userId: int) -> Union["FrontDeskStaff", "Customer", "Admin", "User"]:
        return User.query.get(userId)

# A mixin to be used by Customer and FrontDeskStaff classes for making booking and cancellation of bookings.
class BookingMixin:

    # method to make booking
    def makeBooking(self, booking: Booking) -> Tuple[bool, str]:

        # check if same booking already exists
        seatIds = [seat.id for seat in booking.seats]
        existingBooking = Booking.query.join(Booking.seats).filter(Booking.screeningId == booking.screeningId, 
                       Booking.status != BookingStatus.CANCELLED, CinemaHallSeat.id.in_(seatIds)).first()
        if not existingBooking:
            db.session.add(booking)
            db.session.commit()
            return True, "Booking successfully."
        return False, "Booking already exists."

    # method to cancel a booking
    @staticmethod
    def cancelBooking(booking: Booking) -> Tuple[bool, str]:
        # check if booking exists
        existingBooking = Booking.getBookingById(booking.id)

        # if booking does not exist, return False
        if not existingBooking:
            return False, "Booking does not exist."
        
        # if booking exist but status is calcelled, return False
        elif existingBooking.status == BookingStatus.CANCELLED:
            return False, "Booking already cancelled."
        
        # if booking exists and status is pending, change the status to cancelled, return True
        elif existingBooking.status == BookingStatus.PENDING:
            existingBooking.status = BookingStatus.CANCELLED
            db.session.commit()
            return True, "Booking cancelled successfully."
        
        # if booking exists and status is confirmed, change the status to cancelled, make the refund and return ture
        elif existingBooking.status == BookingStatus.CONFIRMED:
            existingBooking.status = BookingStatus.CANCELLED

            refundAmount = existingBooking.payment.discountedAmount
            
            from .paymentModel import Refund
            Refund.createRefund(existingBooking.payment.id, refundAmount, "Booking Canceled")
            db.session.commit()
            if booking.payment.type == 'cash':
                return True, f"Booking canccelled successfully. Please refund the customer ${refundAmount}."
            else:
                return True, "Booking canccelled successfully and refund has been processed."
        else:
            return False, "Unvalid booking status."

# Admin class
class Admin(User):

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    @property
    def bookings(self):
        raise AttributeError("Admin does not have access to a bookings list.")

    # method to add a movie
    def addMovie(self, newMovie: Movie) -> Tuple[bool, str]:
        # check if the movie already exists
        existingMovie = Movie.query.filter(Movie.title == newMovie.title, Movie.releaseDate == newMovie.releaseDate).first()

        # if the movie doesn't exist, add it to database
        if not existingMovie:
            db.session.add(newMovie)
            db.session.commit()
            return True, "Movie added successfully."
        # otherwise, return false
        return False, "Movie has already been in the database"

    # method to add a screening to a movie
    def addScreening(self, newScreening: Screening) -> Tuple[bool, str]:

        # check if the screening is already in the database
        existingScreening = Screening.query.filter(Screening.screeningDate == newScreening.screeningDate, Screening.startTime == newScreening.startTime, Screening.hallId == newScreening.hallId).first()
        
        # if already in the database, return False
        if existingScreening:
            return False, "Screening already exists."
        
        # if the screening is new, still need to check time crashing and location crashing
        else:
            # generate a list for all the future active screenings
            futureActiveScreeningList = []
            for screening in Screening.query.all():
                if screening.isActiveScreening() and screening.isFutureScreening():
                    futureActiveScreeningList.append(screening)
            # if the screening's time overlaps any of the screenings in the list
            for screening in futureActiveScreeningList:
                if newScreening.screeningDate.date() == screening.screeningDate.date() and newScreening.hallId == screening.hallId and ((newScreening.startTime.time() > screening.startTime.time() and newScreening.startTime.time() < screening.endTime.time()) or (newScreening.endTime.time() > screening.startTime.time() and newScreening.endTime.time() < screening.endTime.time())):
                    return False, "Time crash."
                
            # if no time clash, add it to the databas
            db.session.add(newScreening)

            # add the new screening to the movie's screening list
            movie = Movie.getMovieById(newScreening.movieId)
            if movie.status == MovieStatus.ACTIVE:
                movie.screenings.append(newScreening)
            db.session.commit()
            return True, "Screening added successfully."
        
    # method to cancel a movie
    def cancelMovie(self, movie: Movie) -> Tuple[bool, str]:
        # check if movie existes
        existingMovie = Movie.getMovieById(movie.id)
        if not existingMovie:
            return False, "Movie not found."
        
        # if movie exists but already cancelled
        elif existingMovie.status == MovieStatus.CANCELLED:
            return False, "Movie is already cancelled"
        
        # otherwise do the cancellation in databas
        else:
            movie.status = MovieStatus.CANCELLED

            # cancel all the future active screenings of this movie, too
            for screening in movie.screenings:
                if screening and screening.isFutureScreening() and screening.isActiveScreening():
                    self.cancelScreening(screening)

            db.session.commit()
            return True, "Movie cancelled successfully."

    # method to cancel a screening
    def cancelScreening(self, screening: Screening) -> Tuple[bool, str]:
        # check if screening exists
        existingScreening = Screening.getScreeningById(screening.id)

        # if screening does not exist, return false
        if not existingScreening:
            return False, "Screening not found"
        
        # if screening exist but already canceleed, return false
        elif not screening.isActiveScreening():
            return False, "Screening is already cancelled"
        
        # if screening exists but already finsished, return false
        elif not screening.isFutureScreening():
            return False, "Screening already finished"
        
        # otherwise do the cancellation in databas
        else:
            screening.status = ScreeningStatus.CANCELLED

            # cancel all the avtive bookings of this screening
            for booking in screening.bookings:
                success = BookingMixin.cancelBooking(booking)

                if not success:
                    continue

                else:
                    if booking.user.type == "customer":
                        booking.sendNotification(action="canceled")

            db.session.commit()
            return True, "Screening and its bookings cancelled successfully. Refund being processed."

# FrontDeskStaff class
class FrontDeskStaff(User, BookingMixin):

    __mapper_args__ = {
        'polymorphic_identity': 'staff',
    }

# Customer class
class Customer(User, BookingMixin):
    notifications = db.relationship("Notification", backref='users')

    __mapper_args__ = {
        'polymorphic_identity': 'customer',
    }

    # method to make booking
    def makeBooking(self, booking: Booking) -> bool:
        success, message = super().makeBooking(booking)

        # if booking is successful, add the booking to the customer's bookings list
        if success:
            self.bookings.append(booking)
            db.session.commit()
        return success, message
    
    # method to cancel booking
    def cancelBooking(self, booking: Booking) -> Tuple[bool, str]:
        success, message = super().cancelBooking(booking)

        # if cancel is successful, send notification to the customer
        if success:
            booking.sendNotification(action="canceled")
        return success, message
    
    # method to get the customer's booking list
    def getBookingList(self) -> List[Booking]:
        return Booking.query.filter_by(userId=self.id).order_by(desc(Booking.createdOn)).all()
