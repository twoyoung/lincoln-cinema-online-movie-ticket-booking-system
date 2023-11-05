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


def test_register_failure(test_client, init_database):
    with patch('models.userModel.Guest.register', return_value=(False, 'Username already exists.')):
        response = test_client.post('/auth/signup', data={'username': 'testuser', 'password': 'password123'})
        
        assert response.status_code == 302 
        assert '/auth/signup' in response.headers['Location']
        
        # Now, check if the flash message is as expected
        with test_client.session_transaction() as session:
            flash_messages = dict(session['_flashes'])
            assert 'error' in flash_messages
            assert flash_messages['error'] == 'Username already exists.'
            session.clear()




