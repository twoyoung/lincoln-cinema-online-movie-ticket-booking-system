from flask import Blueprint, jsonify, request, session, url_for, redirect, flash, render_template
from ..controllers import MovieController, AuthController
from functools import wraps

# decorator to limit access to protected pages
# only login user can access
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'userId' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return wrapper

# only admin user can access
def admin_required(f):
    @login_required
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('userType') != 'admin':
            flash("You do not have the required permissions to access this page.")
            return redirect(url_for('movies.home'))
        return f(*args, **kwargs)
    return wrapper

# only customer can access
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

# home page
@movie_bp.route('/', methods=['GET'])
def home():
    return MovieController.browseMovies()

# browse all movies or search for movies
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
    
# display a movie's details and screenings
@movie_bp.route('/movies/<movieId>', methods=['GET', 'POST'])
def showMovieDetailsAndScreenings(movieId):
    return MovieController.viewMovieDetailsAndScreenings(movieId)


# display a screening's seat charts
@movie_bp.route('/book/<screeningId>/seats', methods=['GET', 'POST'])
@login_required
def selectSeats(screeningId):
    if request.method == 'POST':
        selectedSeatIds = request.form.getlist('selectedSeatIds')
        return MovieController.processBooking(session['userId'], screeningId=screeningId, selectedSeatIds=selectedSeatIds)   
    return MovieController.viewSeatChart(screeningId)

# if 'GET', display payment page; if 'POST', get payment information and process booking
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

# get data from javascript code to validate coupon
@movie_bp.route('/api/validate-coupon', methods=['POST'])
def validateCoupon():
    data = request.json
    couponCode = data.get('couponCode')
    return MovieController.validateCouponCode(couponCode)

# display booking confirmation page
@movie_bp.route('/book/<bookingId>/confirm', methods=['GET'])
@login_required
def confirmBooking(bookingId):
    return MovieController.confirmBooking(bookingId=bookingId)

# check all bookings
@movie_bp.route('/bookings', methods=['GET'])
@login_required
def viewBookings():
    return MovieController.viewBookings(session['userId'])

# cancel booking
@movie_bp.route('/cancel/<bookingId>', methods=['POST'])
@login_required
def cancelBooking(bookingId):
    return MovieController.cancelBooking(session['userId'], bookingId)

# if 'GET', display add movie page; if 'POST', get data from input and add a movie
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

# add screening
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

# cancel movie
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
    
# cancel screening
@movie_bp.route('/cancel/screening/<screeningId>', methods=['POST'])
@admin_required
def cancelScreening(screeningId):
    return MovieController.cancelScreening(session['userId'], screeningId)

# work together with javascript code to get notification
@movie_bp.route('/api/get-notifications')
@customer_required
def getNotifications():
    return MovieController.getNotifications(session['userId'])

# work together with javascript code to mark notificaton
@movie_bp.route('/api/mark-notification-read', methods=['POST'])
def markNotificationRead():
    notificationId = request.form['id']
    return MovieController.markNotificationRead(notificationId)

# display sign up page if 'GET' and sign up if 'POST'
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        return AuthController.register(username, password)
    return AuthController.showSignup()

# display login page if 'GET' and login if 'POST'
@auth_bp.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        return AuthController.login(username, password)
    return AuthController.showLogin()

# logout
@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    return AuthController.logout()











    