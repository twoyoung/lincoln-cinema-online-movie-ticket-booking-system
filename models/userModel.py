from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from app import db
from models import Movie, Screening, Booking
from typing import List, Union
from sqlalchemy.orm.exc import NoResultFound
import bcrypt

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
            return Movie.query.filter(Movie.releaseDate.year == rYear).all()
        except NoResultFound:
            return []

    # @classmethod
    # def viewMovieDetails(cls, movieId: int) -> Movie:
    #     try:
    #         return Movie.query.get(movieId)
    #     except NoResultFound:
    #         return None
        # print(f"Title: {aMovie.title}, Language: {aMovie.language}, Genre: {aMovie.genre}, Release Date: {aMovie.releaseDate}, durationMins: {aMovie.durationMins}, country: {aMovie.country}, description: {aMovie.description}")

    @classmethod
    def getMovieById(cls, movieId: int) -> Movie:
        try:
            return Movie.query.get(movieId)
        except NoResultFound:
            return None


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


    def login(self, username: str, password: str) -> bool:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return True
        return False

    def logout(self) -> bool:
        return True
    
    def resetPassword(self, newPassword: str) -> bool:
        self.password = newPassword
        return True
    
    @staticmethod
    def getUserById(userId: int) -> Union["FrontDeskStaff", "Customer", "Admin", "User"]:
        return User.query.get(userId)

class Admin(User):

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }


class FrontDeskStaff(User):

    __mapper_args__ = {
        'polymorphic_identity': 'staff',
    }


class Customer(User):
    bookings = db.relationship("Booking", backref='customer')
    notifications = db.relationship("Notification", backref='customer')
    __mapper_args__ = {
        'polymorphic_identity': 'customer',
    }

    def makeBooking(self, booking: Booking) -> bool:
        if booking not in self.bookings:
            self.bookings.append(booking)
            db.session.add(self.bookings)
            db.session.commit()
            return True
        return False
    
    def cancelBooking(self, booking: Booking) -> bool:
        if booking in self.bookings:
            self.bookings.remove(booking)
            return True
        return False
    
    def getBookingList(self) -> List[Booking]:
        return self.bookings
