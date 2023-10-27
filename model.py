
from typing import List
from abc import ABC
from datetime import date, datetime

allMovies: List["Movie"] = []

allUsers: List["User"] = []

allBookings: List["Booking"] = []


class General(ABC):
    def searchMovieTitle(self, title: str) -> List["Movie"]:
        return [movie for movie in allMovies if movie.title == title]

    def searchMovieLang(self, lang: str) -> List["Movie"]:
        return [movie for movie in allMovies if movie.language == lang]

    def searchMovieGenre(self, genre: str) -> List["Movie"]:
        return [movie for movie in allMovies if movie.genre == genre]

    def searchMovieYear(self, rYear: int) -> List["Movie"]:
        return [movie for movie in allMovies if movie.releaseDate.year == rYear]

    def viewMovieDetails(self, aMovie: "Movie") -> None:
        print(f"Title: {aMovie.title}, Language: {aMovie.language}, Genre: {aMovie.genre}, Release Date: {aMovie.releaseDate}, durationMins: {aMovie.durationMins}, country: {aMovie.country}, description: {aMovie.description}")


class Guest(General, ABC):
    def register(self, username: str, password: str) -> int:
        # for user in allUsers:
        #     if user.username == username:
        pass




class Person(General, ABC):
    def __init__(self, name: str = None, address: str = None, email: str = None, phone: str = None):
        self._name = name
        self._address = address
        self._email = email
        self._phone = phone

    @property
    def name(self) -> str:
        return self._name

    @property
    def address(self) -> str:
        return self._address

    @property
    def email(self) -> str:
        return self._email

    @property
    def phone(self) -> str:
        return self._phone
    

class User(Person, ABC):
    """! The User base class"""
    def __init__(self, username: str, password: str) -> None:
        super().__init__()
        """! The initialiser for User object

        @param username The username of the user account
        @param password The password of the user account
        """
        ## This is the username
        self._username = username
        ## This is the password
        self._password = password

    def login(self) -> bool:
        pass

    def logout(self) -> bool:
        pass

    def resetPassword(self) -> bool:
        pass


class Admin(User):
    """! The Admin derived class represents an admin account"""
    def __init__(self, username: str, password: str):
        """! The initialiser for Admin object
        @param username The username of the admin
        @param password The password of the admin
        @param email The email address of the admin
        """
        ## The base class initialise username, password and email
        super().__init__(username, password)
        ## This is the user type default set as 'admin'

    def addMovie(self, movie: "Movie") -> bool:
        if movie not in allMovies:
            allMovies.append(movie)
            return True
        return False

    def addScreening(self, movie: "Movie", screening: "Screening") -> bool:
        return movie.addScreening(screening)

    def cancelMovie(self, movie: "Movie") -> bool:
        if movie in allMovies:
            allMovies.remove(movie)
            return True
        return False

    def cancelScreening(self, movie: "Movie", screening: "Screening") -> bool:
        if screening in movie.getScreenings():
            movie.getScreenings().remove(screening)
            return True
        return False


class FrontDeskStaff(User):
    """! The Staff derived class represents a front desk staff user account"""
    def __init__(self, username: str, password: str):
        """! The initialiser for Staff object
        @param username The username of the front desk staff account
        @param password The password of the front desk staff acount
        @param email The email address of the front desk staff acount
        """
        ## The base class initialise username, password and email
        super().__init__(username, password)


    def makeBooking(self) -> bool:
        """! The method addBooking for front desk to add booking into the booking list

        @param booking The booking to add to the booking list
        @return A boolean to indicate whether the booking is added successful or not
        """
        pass

    def cancelBooking(self) -> bool:
        """! The method addBooking for front desk staff to remove booking from the booking list

        @param booking The booking to move from the booking list
        @return A boolean to indicate whether the booking is removed successful or not
        """
        pass


class Customer(User):
    """! The Customer derived class represents a customer user account"""
    def __init__(self, username: str, password: str):
        """! The initialiser for Customer object
        @param username The username of the customer
        @param password The password of the customer
        @param email The email address of the customer
        """
        ## The base class initialise username, password and email
        super().__init__(username, password)
        ## This is the booking list under the customer
        self.__bookingList: List[Booking] = []
        ## This is the user type default set as 'customer'
        self.__notificationList: List[Notification] = []

    def makeBooking(self, booking: "Booking") -> bool:
        """! The method addBooking for customer to add booking into the booking list

        @param booking The booking to add to the booking list
        @return A boolean to indicate whether the booking is added successful or not
        """
        if booking not in self.__bookingList:
            self.__bookingList.append(booking)
            return True
        return False

    def cancelBooking(self, booking: "Booking") -> bool:
        """! The method addBooking for customer to remove booking from the booking list

        @param booking The booking to move from the booking list
        @return A boolean to indicate whether the booking is removed successful or not
        """
        if booking in self.__bookingList:
            self.__bookingList.remove(booking)
            return True
        return False

    def getBookingList(self) -> List["Booking"]:
        """! The method findBooking for customer to find a specific booking.

        @param booking The booking to find
        @return The booking to find
        """
        return self.__bookingList


class Movie:
    """! The Movie class maintains information and methods associated to a movie"""
    nextID = 1
    def __init__(self, title: str, language: str, genre: str, releaseDate: datetime, country: str, description: str, durationMins: int):
        """! The initialiser for Movie object

        @param title The title of the movie
        @param language The language of the movie
        @param genre The genre of the movie
        @param releaseDate The release date of the movie
        """
        ## This is the movie ID
        self.__id = User.nextID
        ## This is the title of the movie
        self.__title = title
        ## This is the language of the movie
        self.__language = language
        ## This is the genre of the movie
        self.__genre = genre
        ## This is the release date of the movie
        self.__releaseDate = releaseDate
        self.__description = description
        self.__durationMins = durationMins
        self.__country = country
        ## This is a list of the movie's show arrangement 
        self.__screeningList: List[Screening] = []
        User.nextID += 1

    @property
    def id(self) -> int:
        return self.__id

    @property
    def title(self) -> str:
        return self.__title

    @property
    def language(self) -> str:
        return self.__language

    @property
    def genre(self) -> str:
        return self.__genre

    @property
    def releaseDate(self) -> datetime:
        return self.__releaseDate

    @property
    def description(self) -> str:
        return self.__description

    @property
    def durationMins(self) -> int:
        return self.__durationMins

    @property
    def country(self) -> str:
        return self.__country
    
    @property
    def screeningList(self) -> List["Screening"]:
        return self.__screeningList

    def getScreenings(self) -> List["Screening"]:
        """! The method getScreeningList to return the screening list of the movie

        @return A list of the screenings of the movie
        """
        return self.__screeningList
    
    def addScreening(self, screening: "Screening") -> bool:
        if screening not in self.__screeningList:
            self.__screeningList.append(screening)
            return True
        return False
    
class Screening:
    """! The Screening class maintains information about the show of a particular movie"""
    def __init__(self, screeningDate: datetime, startTime: datetime, endTime: datetime, hall: "CinemaHall"):
        """! The initialiser for Screening object

        @param date The date of the screening
        @param time The time of the screening
        @param hallNumber The location (hall number) of the screening
        @param movie The movie of the screening
        """
        ## This is the date of the screening
        self.__screeningDate = screeningDate
        ## This is the time of the screening
        self.__startTime = startTime
        self.__endTime = endTime
        ## This is the movie of the screening
        self.__hall = hall


class Booking:
    """! The Booking class maintains information about the booking of a ticket"""
    nextID = 1
    def __init__(self, customer: "Customer", numberOfSeats: int, createdOn: date, status: int, screeningSeatInfo: "CinemaHallSeat", screeningDetail: Screening, seats: List["CinemaHallSeat"], orderTotal: float, paymentDetail: "Payment"):
        """! The initialiser for a Booking object
        @param screening The screening for which the booking is made
        @param seats The seats booked
        @param paymentMethod The payment method used for booking
        @param discountCoupon The discount coupon used for booking
        """
        ## This is the booking number
        self.__bookingNum = self.nextID
        ## This is the screening to book
        self.__customer = customer
        ## This is the seats to reserve in the booking
        self.__numberOfSeats = numberOfSeats
        ## This is the payment method for the booking
        self.__createdOn = createdOn
        ## This is the discount coupon used for the booking default set as None
        self.__status = status
        self.__screeningSeatInfo = screeningSeatInfo
        self.__screeningDetail = screeningDetail
        self.__seats = seats
        self.__orderTotal = orderTotal
        self.__paymentDetail = paymentDetail
        Booking.nextID += 1

    def sendNotification(self) -> "Notification":
        notificationContent = f"Booking confirmed for {self.__bookingNum}. Total amount: {self.__orderTotal}"
        return Notification(self.__bookingNum, date.today(), notificationContent)
    

class Notification:
     def __init__(self, notificationID: int, createdOn: date, content: str):
         self.__notificationID = notificationID
         self.createdOn = createdOn
         self.content = content

    
class CinemaHallSeat:
    """! The Seat class maintains information about the seat in a particular hall"""
    def __init__(self, seatNumber: int, seatColumn: int, seatType: int, isReserved: bool, seatPrice: float):
        """! The initialiser for Seat object

        @param row The row letter of the seat
        @param column The column number of the seat
        """
        ## This is the row letter of the seat
        self.__seatNumber = seatNumber
        ## This is the column number of the seat
        self.__seatColumn = seatColumn
        ## This is the hall number of the seat
        self.__seatType = seatType
        ## This is the availability of the seat default set as true
        self.__isReserved = isReserved
        self.__seatPrice = seatPrice

class CinemaHall:
    def __init__(self, name: str, totalSeats: int, listOfSeats: List[CinemaHallSeat]):
        self.name = name
        self.totalSeats = totalSeats
        self.listOfSeats = listOfSeats


class Payment(ABC):
    def __init__(self, amount: float, createdOn: datetime, paymentID: int):
        self._amount = amount
        self._createdOn = createdOn
        self._paymentID = paymentID

    def calcDiscount(self) -> float:
        pass

    def calcFinalPayment(self) -> float:
        pass

class CreditCard(Payment):
    def __init__(self, amount: float, createdOn: datetime, paymentID: int, 
                 creditCardNumber: str, cardType: str, expiryDate: datetime, nameOnCard: str):
        super().__init__(amount, createdOn, paymentID)
        self.__creditCardNumber = creditCardNumber
        self.__cardType = cardType
        self.__expiryDate = expiryDate
        self.__nameOnCard = nameOnCard

class DebitCard(Payment):
    def __init__(self, amount: float, createdOn: datetime, paymentID: int, 
                 cardNumber: str, bankName: str, nameOnCard: str):
        super().__init__(amount, createdOn, paymentID)
        self.__cardNumber = cardNumber
        self.__bankName = bankName
        self.__nameOnCard = nameOnCard

class Coupon:
    def __init__(self, couponID: str, expiryDate: datetime, discount: float):
        self.__couponID = couponID
        self.__expiryDate = expiryDate
        self.__discount = discount
