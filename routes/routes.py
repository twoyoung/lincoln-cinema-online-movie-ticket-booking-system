from flask import Blueprint, jsonify, render_template, request
from controllers import MovieController, authController

movie_bp = Blueprint('movies', __name__)
auth_bp = Blueprint('auth', __name__)

@movie_bp.route('/movies', methods = ['GET', 'POST'])
def showMovies():
    title = request.args.get('title')
    year = request.args.get('year')
    language = request.args.get('language')
    genre = request.args.get('genre')
    if title:
        return MovieController.searchMovies("title", title)
    elif year:
        return MovieController.searchMovies("year", year)
    elif language:
        return MovieController.searchMovies("language", language)
    elif genre:
        return MovieController.searchMovies("genre", genre)
    else:
        return MovieController.browseMovies()
    
@movie_bp.route('/movies/<movieId>', methods=['GET', 'POST'])
def showMovieDetails(movieId):
    return MovieController.viewMovieDetails(movieId)

@movie_bp.route('/movies/<movieId>/screenings', methods=['GET', 'POST'])
def showMovieScreenings(movieId):
    return MovieController.viewMovieScreenings(movieId)

@movie_bp.route('/book/<screeningId>/seats', methods=['GET', 'POST'])
def selectSeats(screeningId):
    if request.method == 'POST':
        selectedSeats = request.form.getlist('selectedSeats')
        return MovieController.processBooking(userId, screeningId=screeningId, selectedSeats=selectedSeats)   
    return MovieController.viewSeatChart(screeningId)

@movie_bp.route('/book/<bookingId>/payment', methods=['GET', 'POST'])
def payment(bookingId):
    if request.method == 'POST':
        pamentData = {
            'bookingId': bookingId,
            
        }
        return MovieController.processBooking(userId, pamentData=pamentData)
    return MovieController.showPaymentPage()




@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        return authController.register(username, password)
    return authController.showSignup()

@auth_bp.route('/login', method = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        return authController.login(username, password)
    return authController.showLogin()









    