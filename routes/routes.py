from flask import Blueprint, request, session, url_for, redirect, flash, render_template
from controllers import MovieController, AuthController
from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'userId' not in session:
            return redirect(url_for('auth_bp.login', next=request.url))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @login_required
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('userType') != 'admin':
            flash("You do not have the required permissions to access this page.")
            return redirect(url_for('movie_bp.showMovies'))
        return f(*args, **kwargs)
    return wrapper


movie_bp = Blueprint('movies', __name__)
auth_bp = Blueprint('auth', __name__)

@movie_bp.route('/', methods=['GET'])
def home():
    return MovieController.browseMovies()

@movie_bp.route('/movies', methods = ['GET', 'POST'])
def showMovies():
    title = request.args.get('title')
    year = request.args.get('year')
    language = request.args.get('language')
    genre = request.args.get('genre')
    if title:
        return MovieController.searchMovies("title", title)
    elif year:
        return MovieController.searchMovies("year", int(year))
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
@login_required
def selectSeats(screeningId):
    if request.method == 'POST':
        selectedSeats = request.form.getlist('selectedSeats')
        return MovieController.processBooking(session['userId'], screeningId=screeningId, selectedSeats=selectedSeats)   
    return MovieController.viewSeatChart(screeningId)

@movie_bp.route('/book/<bookingId>/payment/online', methods=['GET', 'POST'])
@login_required
def paymentOnline(bookingId):
    if request.method == 'POST':
        paymentMethod = request.form.get('paymentMethod')
        useCoupon = request.form.get('useCoupon')
        paymentData = {
            'bookingId': bookingId,
            'paymentMethod': paymentMethod
        }

        if paymentMethod == 'creditcard':
            paymentData['creditCardNumber'] = request.form.get('creditCardNumber')
            paymentData['expiryDate'] = request.form.get('expiryDate')
            paymentData['nameOnCard'] = request.form.get('nameOnCard')

        elif paymentMethod == 'debitcard':
            paymentData['cardNumber'] = request.form.get('cardNumber')
            paymentData['bankName'] = request.form.get('bankName')
            paymentData['nameOnCard'] = request.form.get('nameOnCard')

        if useCoupon:
            paymentData['couponExpiryDate'] = request.form.get('couponExpiryDate')
            paymentData['couponDiscount'] = request.form.get('couponDiscount')


        return MovieController.processBooking(session['userId'], paymentData=paymentData)
    return MovieController.showPaymentPageOnline(bookingId=bookingId)

@movie_bp.route('/book/<bookingId>/payment/onsite', methods=['GET', 'POST'])
@login_required
def paymentOnsite(bookingId):
    if request.method == 'POST':
        paymentMethod = request.form.get('paymentMethod')
        useCoupon = request.form.get('useCoupon')

        if paymentMethod == 'cash':
            paymentData = {
                'bookingId': bookingId,
                'paymentMethod': paymentMethod,
                'receivedCash': request.form.get('receivedCash')
            }

        elif paymentMethod == 'eftPost':
            paymentData = {
                'bookingId': bookingId,
                'paymentMethod': paymentMethod,
            }
        if useCoupon:
            paymentData['couponExpiryDate'] = request.form.get('couponExpiryDate')
            paymentData['couponDiscount'] = request.form.get('couponDiscount')

        return MovieController.processBooking(session['userId'], paymentData=paymentData)
    return MovieController.showPaymentPageInCinema(bookingId=bookingId)

@movie_bp.route('/bookings', methods=['GET'])
@login_required
def viewBookings():
    return MovieController.viewBookings(session['userId'])

@movie_bp.route('/cancel/<bookingId>', methods=['POST'])
@login_required
def cancelBooking(bookingId):
    return MovieController.cancelBooking(session['userId'], bookingId)

@movie_bp.route('/add/movie', methods=['GET', 'POST'])
@admin_required
def addMovie():
    if request.method == 'POST':
        newMovieData = {
            "title": request.form.get('title'),
            "language": request.form.get('language'),
            "genre": request.form.get('genre'),
            "releaseDate": request.form.get('releaseDate'),
            "durationMins": request.form.get('durationMins'),
            "country": request.form.get('country'),
            "description": request.form.get('description')
        }
        return MovieController.addMovie(session['userId'], newMovieData)
    return MovieController.showAddMoviePage()

@movie_bp.route('/add/screening', methods=['GET', 'POST'])
@admin_required
def addScreening():
    if request.method == 'POST':
        newScreeningData = {
            "screeningDate": request.form.get('screeningDate'),
            "startTime": request.form.get('startTime'),
            "endTime": request.form.get('endTime'),
            "hallId": request.form.get('hallId'),
            "movieId": request.form.get('movieId'),
        }
        return MovieController.addScreening(session['userId'], newScreeningData)
    return MovieController.showAddScreeningPage()    

@movie_bp.route('/cancel/movie/<movieId>', methods=['DELETE'])
@admin_required
def cancelMovie(movieId):
    return MovieController.cancelMovie(session['userId'], movieId)

@movie_bp.route('/cancel/screening/<screeningId>', methods=['DELETE'])
@admin_required
def cancelScreening(screeningId):
    return MovieController.cancelScreening(session['userId'], screeningId)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        return AuthController.register(username, password)
    return AuthController.showSignup()

@auth_bp.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        return AuthController.login(username, password)
    return AuthController.showLogin()









    