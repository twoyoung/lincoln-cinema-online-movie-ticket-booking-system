from ..models import Guest, User
from flask import render_template, flash, redirect, url_for, session

class AuthController:

    @staticmethod
    def showSignup():
        return render_template("signup.html", hide_flash_messages=True)

    @staticmethod
    def showLogin():
        return render_template("login.html", hide_flash_messages=True)

    @staticmethod
    def register(username: str, password: str):
        success, message =  Guest.register(username, password)
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')
            return redirect(url_for('auth.signup'))
        
    
    @staticmethod
    def login(username: str, password: str):
        success, message = User.login(username, password)
        if success:
            flash(message, 'success')
            return redirect(url_for('movies.home'))
        else:
            flash(message, 'error')
            return redirect(url_for('auth.login'))
    
    @staticmethod
    def logout() -> bool:
        success, message = User.logout()

        if success:
            flash(message, 'success')
            return redirect(url_for('movies.home'))
        else:
            flash(message, 'danger')
            return redirect(url_for('auth.login'))
    
    @staticmethod
    def resetPassword(password: str) -> bool:
        return User.resetPassword(password)