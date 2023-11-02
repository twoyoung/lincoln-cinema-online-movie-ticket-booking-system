from flask import Blueprint, jsonify, request, session, url_for, redirect, flash, render_template
from controllers import MovieController, AuthController
from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'userId' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @login_required
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('userType') != 'admin':
            flash("You do not have the required permissions to access this page.")
            return redirect(url_for('movies.home'))
        return f(*args, **kwargs)
    return wrapper

def customer_required(f):
    @login_required
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('userType') != 'customer':
            flash("You do not have the required permissions to access this page.")
            return redirect(url_for('movies.home'))
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
def showMovieDetailsAndScreenings(movieId):
    return MovieController.viewMovieDetailsAndScreenings(movieId)


@movie_bp.route('/book/<screeningId>/seats', methods=['GET', 'POST'])
@login_required
def selectSeats(screeningId):
    if request.method == 'POST':
        selectedSeatIds = request.form.getlist('selectedSeatIds')
        return MovieController.processBooking(session['userId'], screeningId=screeningId, selectedSeatIds=selectedSeatIds)   
    return MovieController.viewSeatChart(screeningId)

@movie_bp.route('/book/<bookingId>/payment/online', methods=['GET', 'POST'])
@customer_required
def paymentOnline(bookingId):
    if request.method == 'POST':
        paymentMethod = request.form.get('paymentMethod')
        couponCode = request.form.get('couponCode')
        paymentData = {
            'bookingId': bookingId,
            'paymentMethod': paymentMethod,
            'couponCode': couponCode
        }

        if paymentMethod == 'creditcard':
            paymentData['creditCardNumber'] = request.form.get('creditCardNumber')
            paymentData['expiryDate'] = request.form.get('expiryDate')
            paymentData['nameOnCard'] = request.form.get('nameOnCard')

        elif paymentMethod == 'debitcard':
            paymentData['debitCardNumber'] = request.form.get('debitCardNumber')
            paymentData['bankName'] = request.form.get('bankName')
            paymentData['nameOnCard'] = request.form.get('nameOnCard')

        return MovieController.processBooking(session['userId'], paymentData=paymentData)
    return MovieController.showPaymentPageOnline(bookingId=bookingId)

@movie_bp.route('/book/<bookingId>/payment/onsite', methods=['GET', 'POST'])
@login_required
def paymentOnsite(bookingId):
    if request.method == 'POST':
        paymentMethod = request.form.get('paymentMethod')
        couponCode = request.form.get('couponCode')

        if paymentMethod == 'cash':
            paymentData = {
                'bookingId': bookingId,
                'paymentMethod': paymentMethod,
                'receivedCash': request.form.get('receivedCash'),
                'change': request.form.get('change'),
                'couponCode': couponCode
            }
            print(paymentData)

        elif paymentMethod == 'eftpos':
            paymentData = {
                'bookingId': bookingId,
                'paymentMethod': paymentMethod,
                'couponCode': couponCode
            }

        return MovieController.processBooking(session['userId'], paymentData=paymentData)
    return MovieController.showPaymentPageOnsite(bookingId=bookingId)

@movie_bp.route('/api/validate-coupon', methods=['POST'])
def validateCoupon():
    data = request.json
    couponCode = data.get('couponCode')
    return MovieController.validateCouponCode(couponCode)

@movie_bp.route('/book/<bookingId>/confirm', methods=['GET'])
@login_required
def confirmBooking(bookingId):
    return MovieController.confirmBooking(bookingId=bookingId)

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

@movie_bp.route('/add/movie/<movieId>/screening', methods=['POST'])
@admin_required
def addScreening(movieId):
    newScreeningData = {
        "screeningDate": request.form.get('screeningDate'),
        "startTime": request.form.get('startTime'),
        "endTime": request.form.get('endTime'),
        "hallId": request.form.get('hallId'),
        "movieId": movieId
    }
    return MovieController.addScreening(session['userId'], newScreeningData) 

@movie_bp.route('/cancel/movie', methods=['GET'])
@movie_bp.route('/cancel/movie/<movieId>', methods=['GET', 'POST'])
@admin_required
def cancelMovie(movieId=None):
    if movieId and request.method == 'POST':
        return MovieController.cancelMovie(session['userId'], movieId)
    elif movieId:
        return redirect(url_for('movies.showMovieDetails',movieId=movieId))
    else:
        return MovieController.showCancelMoviePage()

@movie_bp.route('/cancel/screening/<screeningId>', methods=['POST'])
@admin_required
def cancelScreening(screeningId):
    return MovieController.cancelScreening(session['userId'], screeningId)

@movie_bp.route('/api/get-notifications')
@customer_required
def getNotifications():
    return MovieController.getNotifications(session['userId'])

@movie_bp.route('/api/mark-notification-read', methods=['POST'])
def markNotificationRead():
    notificationId = request.form['id']
    return MovieController.markNotificationRead(notificationId)


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

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    return AuthController.logout()











    