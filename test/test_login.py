from unittest.mock import patch
from flask import url_for, get_flashed_messages


def test_register_successful(test_client, init_database):
    with patch('models.userModel.Guest.register', return_value=(True, 'Registered successfully.')):
        response = test_client.post('/auth/signup', data={'username': 'testuser', 'password': 'password123'})
        
        assert response.status_code == 302 
        assert '/auth/login' in response.headers['Location']
        
        # Now, check if the flash message is as expected
        with test_client.session_transaction() as session:
            flash_messages = dict(session['_flashes'])
            assert 'success' in flash_messages
            assert flash_messages['success'] == 'Registered successfully.'
            session.clear()

def test_login_successful(test_client, init_database):
    with patch('models.userModel.User.login', return_value=(True, "Logged in successfully.")):
        response = test_client.post('/auth/login', data={'username': 'testuser', 'password': 'password123'})
        assert response.status_code == 302 
        assert '/' in response.headers['Location']
        
        # Now, check if the flash message is as expected
        with test_client.session_transaction() as session:
            # assert 'userId' in session
            # assert 'userType' in session
            # print(session)

            flash_messages = dict(session['_flashes'])
            assert 'success' in flash_messages
            assert flash_messages['success'] == 'Logged in successfully.'
            session.clear()

def test_login_failure_1(test_client, init_database):
    with patch('models.userModel.User.login', return_value=(False, "Username not found.")):
        response = test_client.post('/auth/login', data={'username': 'testuser1', 'password': 'password1234'})
        
        assert response.status_code == 302 
        assert '/auth/login' in response.headers['Location']
        
        # Now, check if the flash message is as expected
        with test_client.session_transaction() as session:
            flash_messages = dict(session['_flashes'])
            assert 'error' in flash_messages
            assert flash_messages['error'] == "Username not found."
            session.clear()


def test_login_failure_2(test_client, init_database):
    with patch('models.userModel.User.login', return_value=(False, "Incorrect password.")):
        response = test_client.post('/auth/login', data={'username': 'testuser', 'password': 'password1234'})
        
        assert response.status_code == 302 
        assert '/auth/login' in response.headers['Location']
        
        # Now, check if the flash message is as expected
        with test_client.session_transaction() as session:
            flash_messages = dict(session['_flashes'])
            assert 'error' in flash_messages
            assert flash_messages['error'] == "Incorrect password."
            session.clear()



