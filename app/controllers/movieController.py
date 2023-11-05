from flask import jsonify, redirect, render_template, url_for, flash, get_flashed_messages, session
from sqlalchemy import desc
from ..models import General, User, Movie, CinemaHallSeat, Booking, BookingStatus, Payment, Screening, CreditCard, DebitCard, Coupon, CashPayment, Eftpos, Notification, MovieStatus
from typing import List
from datetime import datetime
from collections import defaultdict

# MovieController class
class MovieController:

    # method to browser all movies
    @staticmethod
    def browseMovies():
        allMovies = General.getAllMovies()
        return render_template("index.html", allMovies=allMovies)
    
    # method to search movies
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

    # method to view movie details and it's screenings schedules
    @staticmethod
    def viewMovieDetailsAndScreenings(movieId: int):
        movie = Movie.getActiveMovieById(movieId)
        if movie:
            screeningList = movie.getScreenings()

            # Organize screenings data by date
            screeningsByDate = defaultdict(list)
            for screening in screeningList:
                screeningsByDate[screening.screeningDate.date()].append(screening)

            # Check if 'userType' exists in session. If not, default to 'guest'
            userType = session.get('userType', 'guest')
            dateList = list(sorted(screeningsByDate.keys(), reverse=False))
            if dateList == []:
                dateList = ['---']
            return render_template("movieDetailsAndScreenings.html", dateList=dateList, screeningsByDate=screeningsByDate, movie=movie, userType=userType)
        else:
            flash("Movie does not exist or has been cancelled.", 'error')
            return redirect(url_for('movies.showMovies'))

    # method to view seat chart of the screening  
    @staticmethod
    def viewSeatChart(screeningId: int):
        # get the screening by id
        screening = Screening.getActiveScreeningById(screeningId)
        if screening:
            # get the screening's seat chart
            seatMatrix = screening.getSeatChart()
            return render_template("seatChart.html", seatMatrix=seatMatrix, screeningId=screeningId)
        else:
            return "Screening not found", 404

    # method to display the payment online page (for customer booking online)
    @staticmethod
    def showPaymentPageOnline(bookingId: int):
        booking = Booking.getBookingById(bookingId)
        return render_template("paymentOnline.html", booking=booking)
    
    # method to display the payment onsite page (for staff booking onsite)
    @staticmethod
    def showPaymentPageOnsite(bookingId: int):
        booking = Booking.getBookingById(bookingId)
        return render_template("paymentOnsite.html", booking=booking)

    # method to process booking and payment
    @staticmethod
    def processBooking(userId: int, screeningId: int = None, selectedSeatIds: List[str] = None, paymentData = None):
        user = User.getUserById(userId)
        # if passed data is about selected seats, make the booking
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
            screening = Screening.getActiveScreeningById(screeningId)
            booking.screening = screening
            booking.numberOfSeats = len(selectedSeats)
            booking.createdOn = datetime.now()
            booking.orderTotal = round(sum(seat.seatPrice for seat in selectedSeats),2)
            booking.seats = selectedSeats

            if user.type == 'customer':
                success, message = user.makeBooking(booking)
                # if booking is successful, redirect to the payment page
                if success:
                    return redirect(url_for('movies.paymentOnline', bookingId = booking.id))
                else:
                    flash(message, 'error')
                    return redirect(url_for('movies.selectSeats', screeningId = screeningId))
            elif user.type == 'staff':
                success, message = user.makeBooking(booking)
                # if booking is successful, redirect to the payment page
                if success:
                    return redirect(url_for('movies.paymentOnsite', bookingId = booking.id))
                else:
                    flash(message, 'error')
                    return redirect(url_for('movies.selectSeats', screeningId = screeningId))
            
        # if passed data is payment data, make the payment
        elif paymentData:
            booking = Booking.getBookingById(paymentData['bookingId'])
            if not booking:
                return "Booking not found", 404
            
            # based on different payment methods, create different payment objects
            if paymentData['paymentMethod'] == 'creditcard':
                payment = CreditCard(
                    originalAmount=booking.orderTotal,
                    discountedAmount=booking.orderTotal,
                    createdOn = datetime.now(),
                    type = 'creditcard',
                    booking = booking,
                    creditCardNumber = paymentData['creditCardNumber'],
                    expiryDate = paymentData['expiryDate'],
                    nameOnCard = paymentData['nameOnCard'],
                )
            elif paymentData['paymentMethod'] == 'debitcard':
                payment = DebitCard(
                    originalAmount = booking.orderTotal,
                    discountedAmount=booking.orderTotal,
                    type = 'debitcard',
                    createdOn = datetime.now(),
                    booking = booking,
                    cardNumber = paymentData['debitCardNumber'],
                    bankName = paymentData['bankName'],
                    nameOnCard = paymentData['nameOnCard']
                )

            elif paymentData['paymentMethod'] == 'cash':
                payment = CashPayment(
                    originalAmount = booking.orderTotal,
                    discountedAmount=booking.orderTotal,
                    receivedCash = paymentData['receivedCash'],
                    change = paymentData['change'],
                    type = 'cash',
                    createdOn = datetime.now(),
                    booking = booking,
                )

            elif paymentData['paymentMethod'] == 'eftpos':
                payment = Eftpos(
                    originalAmount = booking.orderTotal,
                    discountedAmount=booking.orderTotal,
                    type = 'eftpos',
                    createdOn = datetime.now(),
                    booking = booking,
                )

            else:
                return "Invalid payment method", 400
            
            # check if coupon code is valid, append it to the payment object
            if Coupon.couponIsValid(paymentData['couponCode']):
                coupon = Coupon.getCouponByCode(paymentData['couponCode'])
                payment.couponId = coupon.id
                payment.coupon = coupon

            # make the payment
            success, message = Payment.createPayment(payment)
            if success:
                flash(message, 'success')   
                return redirect(url_for('movies.confirmBooking', bookingId = booking.id))
            else:
                flash(message, 'error')
                return redirect(url_for('movies.viewBookings'))

        else:
            return "Invalid booking data", 400
        
    # method to validate the coupon code
    @staticmethod
    def validateCouponCode(couponCode: str):
        if Coupon.couponIsValid(couponCode):
            coupon = Coupon.getCouponByCode(couponCode)
            return jsonify(valid=True, discount=coupon.discount)
        else:
            return jsonify(valid=False, discount=0)

    # method to display booking confirmation page   
    @staticmethod
    def confirmBooking(bookingId: int):
        booking = Booking.getBookingById(bookingId)
        return render_template("bookingConfirm.html", booking=booking)
    
    # method to get user's notification list
    @staticmethod
    def getNotifications(userId: int):
        user = User.getUserById(userId)
        if user and user.type == 'customer':
            notificationList = Notification.query.filter_by(userId=userId).order_by(desc(Notification.timestamp)).all() # ordered by timestamp with newest notification first
            numberOfUnreadNotifications = Notification.numberOfUnreadNotifications()
            # Convert the list of notifications into a list of dictionaries
            notifications = [
                {
                    'id': notification.id,
                    'message': notification.message,
                    'isRead': notification.isRead,
                    # Add more fields as needed
                }
                for notification in notificationList
            ]
            return jsonify(numberOfUnreadNotifications=numberOfUnreadNotifications, notifications=notifications)
        
    # method to mark a notification as read
    @staticmethod
    def markNotificationRead(notificationId: int):
        notification = Notification.getNotificationById(notificationId)
        if notification:
            notification.markRead()
            return jsonify(success=True)
        return jsonify(success=False)

    # method to view the booking list
    @staticmethod
    def viewBookings(userId: int):
        user = User.getUserById(userId)
        if user.type == "customer":
            bookingList = user.getBookingList()
        if user.type == "staff":
            bookingList = Booking.getAllBookings()
        return render_template('bookings.html', bookingList=bookingList)
            
    # method to cancel a booking
    @staticmethod
    def cancelBooking(userId: int, bookingId: int):
        booking = Booking.getBookingById(bookingId)
        user = User.getUserById(userId)
        if user.type == 'customer' or user.type == 'staff':
            success, message = user.cancelBooking(booking)
            if success:
                flash(message, 'success')
            else:
                flash(message, 'error')
            return redirect(url_for('movies.viewBookings'))
        else:
            flash("Unauthorized access", 'error')
            return redirect(url_for('movies.viewBookings'))

    # method to show add movie page
    @staticmethod
    def showAddMoviePage():
        return render_template('addMovie.html')
    
    # method to add movie
    @staticmethod
    def addMovie(userId: int, newMovieData: dict):
        user = User.getUserById(userId)
        newMovie = Movie(
            title = newMovieData['title'],
            language = newMovieData['language'],
            genre = newMovieData['genre'],
            releaseDate = datetime.strptime(newMovieData['releaseDate'], '%Y-%m-%d'),
            durationMins = newMovieData['durationMins'],
            country = newMovieData['country'],
            description = newMovieData['description']
        )
        success, message = user.addMovie(newMovie)
        if success:
            flash(message, 'success')
            return redirect(url_for('movies.showMovieDetailsAndScreenings', movieId = newMovie.id))
        else:
            flash(message, 'error')
            return redirect(url_for('movies.addMovie'))
       
    # method to add screening to a movie
    @staticmethod
    def addScreening(userId: int, newScreeningData: dict):
        user = User.getUserById(userId)
        newScreening = Screening(
            screeningDate = datetime.strptime(newScreeningData['screeningDate'], '%Y-%m-%d'),
            startTime = datetime.strptime(newScreeningData['startTime'],'%H:%M'),
            endTime = datetime.strptime(newScreeningData['endTime'],'%H:%M'),
            hallId = newScreeningData['hallId'],
            movieId = newScreeningData['movieId']
        )
        success, message =  user.addScreening(newScreening)
        if success:
            flash(message, 'success')
            
        else:
            flash(message, 'error')
        return redirect(url_for('movies.showMovieDetailsAndScreenings', movieId = newScreeningData['movieId']))
    
    # method to show cancel movie page
    @staticmethod
    def showCancelMoviePage():
        movies = Movie.query.all()
        return render_template("cancelMovie.html", movies=movies)
        
    # method to cancel a movie
    @staticmethod
    def cancelMovie(userId: int, movieId: int):
        user = User.getUserById(userId)
        movie = Movie.getMovieById(movieId)
        if movie:
            success, message = user.cancelMovie(movie)
            if success:
                flash(message, 'success')
                return redirect(url_for('movies.cancelMovie'))
            else:
                flash(message, 'error')
                return redirect(url_for('movies.cancelMovie'))
        else:
            flash("Movie not found", 'error')
            return redirect(url_for('movies.cancelMovie'))

    # method to cancel a screening
    @staticmethod
    def cancelScreening(userId: int, screeningId: int):
        user = User.getUserById(userId)
        screening = Screening.getScreeningById(screeningId)
        success, message = user.cancelScreening(screening)
        
        if success:
            flash(message, 'success')

        else:
            flash(message, 'error')
        
        return redirect(url_for('movies.showMovieDetailsAndScreenings', movieId=screening.movie.id))


        





    




            

        

            

            



        
    
        
    
        
    
