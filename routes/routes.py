from flask import Blueprint, jsonify, render_template, request, session
from controllers import MovieController, AuthController

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
        return MovieController.processBooking(session['userId'], screeningId=screeningId, selectedSeats=selectedSeats)   
    return MovieController.viewSeatChart(screeningId)

@movie_bp.route('/book/<bookingId>/payment/online', methods=['GET', 'POST'])
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

@movie_bp.route('/bookings', method=['GET'])
def viewBookings():
    return MovieController.viewBookings(session['userId'])

@movie_bp.route('/cancel/<bookingId>', methods=['POST'])
def cancelBooking(bookingId):
    return MovieController.cancelBooking(session['userId'], bookingId)

@movie_bp.route('/add/movie', methods=['GET', 'POST'])
def addMovie():
    if request.method == 'POST':
        newMovieData = {
            "title": request.POST.get('title'),
            "language": request.POST.get('language'),
            "genre": request.POST.get('genre'),
            "releaseDate": request.POST.get('releaseDate'),
            "durationMins": request.POST.get('durationMins'),
            "country": request.POST.get('country'),
            "description": request.POST.get('description')
        }
        return MovieController.addMovie(session['userId'], newMovieData)
    return MovieController.showAddMoviePage()

@movie_bp.route('/add/screening', methods=['GET', 'POST'])
def addScreening():
    if request.method == 'POST':
        newScreeningData = {
            "screeningDate": request.POST.get('screeningDate'),
            "startTime": request.POST.get('startTime'),
            "endTime": request.POST.get('endTime'),
            "hallId": request.POST.get('hallId'),
            "MovieId": request.POST.get('movieId'),
        }
        return MovieController.addScreening(session['userId'], newScreeningData)
    return MovieController.showAddScreeningPage()    

@movie_bp.route('/cancel/movie/<movieId>', methods=['GET', 'POST'])
def cancelMovie(movieId):
    return MovieController.cancelMovie(session['userId'], movieId)

@movie_bp.route('/cancel/screening/<screeningId>', methods=['GET', 'POST'])
def cancelScreening(screeningId):
    return MovieController.cancelScreening(session['userId'], screeningId)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        return AuthController.register(username, password)
    return AuthController.showSignup()

@auth_bp.route('/login', method = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        return AuthController.login(username, password)
    return AuthController.showLogin()









    