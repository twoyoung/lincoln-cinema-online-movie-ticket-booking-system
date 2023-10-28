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
    def register(self, username: str, password: str) -> bool:
        return Guest.register(self, username, password)
    
    @staticmethod
    def login(self, username: str, password: str) -> bool:
        return User.login(self, username, password)
    
    @staticmethod
    def logout(self) -> bool:
        return User.logout(self)
    
    @staticmethod
    def resetPassword(self, password: str) -> bool:
        return User.resetPassword(self, password)