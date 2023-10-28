from flask import redirect, session, render_template, url_for
from models import General, User, Movie, CinemaHallSeat, Booking, BookingStatus
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
        screening = General.getScreeningById(screeningId)
        if screening:
            seatChart = screening.getSeatChart()
            return render_template("seatChart.html", seatChart=seatChart)
        else:
            return "Screening not found", 404

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

            if user.type == 'staff' or user.type == 'customer':
                user.makeBooking(booking)

            if user.type == 'customer':
                return redirect(url_for('movie_bp.payment', bookingId = booking.bookingId))
        elif paymentData:
            booking = Booking.query.get(paymentData['bookingId'])
            if not booking:
                return "Booking not found", 404
            
            booking.status = BookingStatus.CONFIRMED
            db.session.commit()

            return "Booking confirmed", 200
        else:
            return "Invalid booking data", 400
            

        

            

            



        
    
        
    
        
    
