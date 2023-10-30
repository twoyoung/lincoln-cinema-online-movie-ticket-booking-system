from flask import redirect, render_template, url_for
from models import General, User, Movie, CinemaHallSeat, Booking, BookingStatus, Payment, Screening, CreditCard, DebitCard, Coupon, CashPayment, Eftpos
from typing import List
from datetime import datetime

class MovieController:
    @staticmethod
    def browseMovies():
        allMovies = General.getAllMovies()
        return render_template("index.html", allMovies=allMovies)
    
    @staticmethod
    def searchMovies(criteria: str, value: str):
        if criteria == "title":
            filteredMovies = General.searchMovieTitle(value)
        elif criteria == "language":
            filteredMovies = General.searchMovieLang(value)
        elif criteria == "genre":
            filteredMovies = General.searchMovieGenre(value)
        elif criteria == "year":
            filteredMovies = General.searchMovieYear(value)
            print(filteredMovies)
        return render_template("index.html", allMovies=filteredMovies)

    @staticmethod
    def viewMovieDetails(movieId: int):
        movie = Movie.getMovieById(movieId)
        if movie:
            return render_template("movie_details.html", movie=movie)
        else:
            return "Movie not found", 404
    
    @staticmethod
    def viewMovieScreenings(movieId: int):
        movie = Movie.getMovieById(movieId)
        if movie:
            screeningList = movie.screenings
        else:
            screeningList = []
        return render_template("movieScreenings.html", screeningList=screeningList)
        
    @staticmethod
    def viewSeatChart(screeningId: int):
        screening = Screening.getScreeningById(screeningId)
        if screening:
            seatMatrix = screening.getSeatChart()
            return render_template("seatChart.html", seatMatrix=seatMatrix, screeningId=screeningId)
        else:
            return "Screening not found", 404
        
    @staticmethod
    def showPaymentPageOnline(bookingId: int):
        booking = Booking.getBookingById(bookingId)
        return render_template("paymentOnline.html", booking=booking)
    
    @staticmethod
    def showPaymentPageOnsite(bookingId: int):
        booking = Booking.getBookingById(bookingId)
        return render_template("paymentOnsite.html", booking=booking)

    @staticmethod
    def processBooking(userId: int, screeningId: int = None, selectedSeatIds: List[str] = None, paymentData = None):
        user = User.getUserById(userId)
        if selectedSeatIds:
            selectedSeats = []
            seatIdString = selectedSeatIds[0].split(',')
            seatIds = [int(seatId) for seatId in seatIdString]
            for seatId in seatIds:
                selectedSeats.append(CinemaHallSeat.getSeatById(seatId))
            booking = Booking()
            booking.userId = userId
            booking.user = user
            booking.screeningId = screeningId
            booking.status = BookingStatus.PENDING
            screening = Screening.getScreeningById(screeningId)
            booking.screening = screening
            booking.numberOfSeats = len(selectedSeats)
            booking.createdOn = datetime.now()
            booking.orderTotal = sum(seat.seatPrice for seat in selectedSeats)
            booking.seats = selectedSeats

            if user.type == 'customer':
                user.makeBooking(booking)
                print(booking.id)
                return redirect(url_for('movies.paymentOnline', bookingId = booking.id))
            elif user.type == 'staff':
                user.makeBooking(booking)
                print(booking.id)
                return redirect(url_for('movies.paymentOnsite', bookingId = booking.id))
            
        elif paymentData:
            booking = Booking.getBookingById(paymentData['bookingId'])
            if not booking:
                return "Booking not found", 404
            
            if paymentData['paymentMethod'] == 'creditcard':
                payment = CreditCard(
                    originalAmount=booking.orderTotal,
                    discountedAmount=booking.orderTotal,
                    createdOn = datetime.now(),
                    type = paymentData['cardType'],
                    bookingId = paymentData['bookingId'],
                    booking = booking,
                    creditCardNumber = paymentData['creditCardNumber'],
                    expiryDate = paymentData['expiryDate'],
                    nameOnCard = paymentData['nameOnCard'],
                )
            elif paymentData['paymentMethod'] == 'debitcard':
                payment = DebitCard(
                    originalAmount = booking.orderTotal,
                    discountedAmount=booking.orderTotal,
                    createdOn = datetime.now(),
                    bookingId = paymentData['bookingId'],
                    booking = booking,
                    cardNumber = paymentData['cardNumber'],
                    bankName = paymentData['bankName'],
                    nameOnCard = paymentData['nameOnCard']
                )

            elif paymentData['paymentMethod'] == 'cash':
                payment = CashPayment(
                    originalAmount = booking.orderTotal,
                    discountedAmount=booking.orderTotal,
                    createdOn = datetime.now(),
                    bookingId = paymentData['bookingId'],
                    booking = booking,
                )

            elif paymentData['paymentMethod'] == 'eftPos':
                payment = CashPayment(
                    originalAmount = booking.orderTotal,
                    discountedAmount=booking.orderTotal,
                    createdOn = datetime.now(),
                    bookingId = paymentData['bookingId'],
                    booking = booking,
                )

            else:
                return "Invalid payment method", 400
            
            if 'couponExpiryDate' in paymentData and 'couponDiscount' in paymentData:
                coupon = Coupon(
                    expiryDate = paymentData['couponExpiryDate'],
                    discount=paymentData['couponDiscount']
                )
                payment.coupon = coupon
            
            Payment.createPayment(payment)
                
            return "Booking confirmed", 201

        else:
            return "Invalid booking data", 400
        
    @staticmethod
    def viewBookings(userId: int):
        user = User.getUserById(userId)
        if user.type == "customer":
            return user.getBookingList()
        if user.type == "staff":
            return Booking.getBookingList()
            
    @staticmethod
    def cancelBooking(userId: int, bookingId: int):
        booking = Booking.getBookingById(bookingId)
        user = User.getUserById(userId)
        if user.type == 'customer' or user.type == 'staff':
            return user.cancelBooking(booking)

    @staticmethod
    def showAddMoviePage():
        return render_template('addMovie.html')
    
    @staticmethod
    def addMovie(userId: int, newMovieData: dict):
        user = User.getUserById(userId)
        if user.type == 'admin':
            newMovie = Movie(
                title = newMovieData['title'],
                language = newMovieData['language'],
                genre = newMovieData['genre'],
                releaseDate = newMovieData['releaseDate'],
                durationMins = newMovieData['durationMins'],
                country = newMovieData['country'],
                description = newMovieData['description']
            )
            return user.addMovie(newMovie)
        else:
            return "Unauthorized", 401

    @staticmethod
    def showAddScreeningPage():
        return render_template('addScreening.html')
    
    @staticmethod
    def addScreening(userId: int, newScreeningData: dict):
        user = User.getUserById(userId)
        if user.type == 'admin':
            newScreening = Screening(
                screeningDate = newScreeningData['screeningDate'],
                startTime = newScreeningData['startTime'],
                endTime = newScreeningData['endTime'],
                hallId = newScreeningData['hallId'],
                movieId = newScreeningData['movieId']
            )
            return user.addScreening(newScreening)
        else:
            return "Unauthorized", 401
        
    @staticmethod
    def cancelMovie(userId: int, movieId: int):
        user = User.getUserById(userId)
        if user.type == 'admin':
            movie = Movie.getMovieById(movieId)
            return user.cancelMovie(movie)
        else:
            return "Unauthorized", 401
        
    @staticmethod
    def cancelScreening(userId: int, screeningId: int):
        user = User.getUserById(userId)
        if user.type == 'admin':
            screening = Screening.getScreeningById(screeningId)
            return user.cancelScreening(screening)
        else:
            return "Unauthorized", 401


        





    




            

        

            

            



        
    
        
    
        
    
