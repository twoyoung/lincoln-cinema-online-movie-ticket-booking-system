from flask import redirect, session, render_template, url_for
from models import General, User, Movie, CinemaHallSeat, Booking, BookingStatus, Payment, Screening, CreditCard, DebitCard, Coupon, CashPayment, Eftpos
from typing import List
from datetime import datetime


class MovieController:
    def browseMovies(self):
        allMovies = General.getAllMovies()
        return render_template("index.html", allMovies=allMovies)
    
    def searchMovies(self, criteria: str, value: str):
        if criteria == "title":
            filteredMovies = General.searchMovieTitle(value)
        elif criteria == "language":
            filteredMovies = General.searchMovieLang(value)
        elif criteria == "genre":
            filteredMovies = General.searchMovieGenre(value)
        elif criteria == "year":
            filteredMovies = General.searchMovieYear(value)
        return render_template("index.html", filteredMovies=filteredMovies)

    def viewMovieDetails(self, movieId: int):
        movie = General.getMovieById(movieId)
        if movie:
            return render_template("movie_details.html", movie=movie)
        else:
            return "Movie not found", 404
    
    def viewMovieScreenings(self, movieId: int):
        movie = General.getMovieById(movieId)
        if movie:
            screeningList = movie.screenings
        else:
            screeningList = []
        return render_template("movieScreenings.html", screeningList=screeningList)
        

    def viewSeatChart(self, screeningId: int):
        screening = Screening.getScreeningById(screeningId)
        if screening:
            seatChart = screening.getSeatChart()
            return render_template("seatChart.html", seatChart=seatChart)
        else:
            return "Screening not found", 404
        
    def showPaymentpageOnline(self, bookingId: int):
        booking = Booking.getBookingById(bookingId)
        return render_template("paymentOnline.html", booking=booking)
    
    def showPaymentpageOnsite(self, bookingId: int):
        booking = Booking.getBookingById(bookingId)
        return render_template("paymentOnsite.html", booking=booking)

    def processBooking(self, userId: int, screeningId: int = None, selectedSeats: List[CinemaHallSeat] = None, paymentData = None):
        user = User.getUserById(userId)
        if selectedSeats:
            booking = Booking()
            booking.userId = userId
            booking.user = user
            booking.screeningId = screeningId
            booking.status = BookingStatus.PENDING
            screening = General.getScreeningById(screeningId)
            booking.screening = screening
            booking.numberOfSeats = len(selectedSeats)
            booking.createdOn = datetime.now()
            booking.orderTotal = sum(seat.seatPrice for seat in selectedSeats)
            booking.seats = selectedSeats

            if user.type == 'customer':
                user.makeBooking(booking)
                return redirect(url_for('movie_bp.paymentOnline', bookingId = booking.bookingId))
            elif user.type == 'staff':
                user.makeBooking(booking)
                return redirect(url_for('movie_bp.paymentOnsite', bookingId = booking.bookingId))
            
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

            elif paymentData['paymentMethod'] == 'eftPost':
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
                
            return "Booking confirmed", 200

        else:
            return "Invalid booking data", 400
        
    def viewBookings(self, userId: int):
        user = User.getUserById(userId)
        if user.type == "customer":
            return user.getBookingList()
        if user.type == "staff":
            return Booking.getBookingList()
            
        
    def cancelBooking(self, userId: int, bookingId: int):
        booking = Booking.getBookingById(bookingId)
        user = User.getUserById(userId)
        if user.type == 'customer' or user.type == 'staff':
            user.cancelBooking(booking)

    




            

        

            

            



        
    
        
    
        
    
