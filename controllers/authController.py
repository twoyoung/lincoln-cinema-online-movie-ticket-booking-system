from models import Guest, User
from flask import render_template

class AuthController:

    @staticmethod
    def showSignup():
        return render_template("signup.html")

    @staticmethod
    def showLogin():
        return render_template("login.html")

    @staticmethod
    def register(username: str, password: str) -> bool:
        return Guest.register(username, password)
    
    @staticmethod
    def login(username: str, password: str) -> bool:
        return User.login(username, password)
    
    @staticmethod
    def logout() -> bool:
        return User.logout()
    
    @staticmethod
    def resetPassword(password: str) -> bool:
        return User.resetPassword(password)