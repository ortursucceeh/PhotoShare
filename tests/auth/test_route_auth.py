import sys
import os
from unittest.mock import MagicMock

from src.database.models import User
from src.conf.messages import ALREADY_EXISTS, EMAIL_NOT_CONFIRMED, INVALID_PASSWORD, INVALID_EMAIL, USER_NOT_ACTIVE

sys.path.append(os.getcwd())


def test_create_user(client, user, monkeypatch):
    """
    The test_create_user function tests the /api/auth/signup endpoint.
    It does so by creating a user and then checking that the response is 201,
    that the email address matches what was sent in, and that an id was returned.
    
    :param client: Make requests to the flask application
    :param user: Pass in the user data from the fixture
    :param monkeypatch: Mock the send_email function
    :return: A response object
    """
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.confirmed_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


def test_repeat_create_user(client, user):
    """
    The test_repeat_create_user function tests that a user cannot be created twice.
        It does this by creating a user, then attempting to create the same user again.
        The second attempt should fail with an HTTP 409 status code and an error message.
    
    :param client: Make requests to the application
    :param user: Pass the user data to the test function
    :return: The status code 409 and the detail already_exists
    """
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == ALREADY_EXISTS


def test_login_user_not_confirmed(client, user):
    """
    The test_login_user_not_confirmed function tests that a user cannot login if they have not confirmed their email address.
    
    
    :param client: Make requests to the flask application
    :param user: Create a user object that is passed to the function
    :return: A 401 status code and a json response with the detail key set to email_not_confirmed
    """
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == EMAIL_NOT_CONFIRMED
    

def test_login_user(client, session, user):
    """
    The test_login_user function tests the login_user function in the auth.py file.
    It does this by first creating a user, then verifying that user's email address, and finally logging in with that 
    user's credentials.
    
    :param client: Make requests to the flask application
    :param session: Access the database
    :param user: Get the user data from the fixture
    :return: A response object
    """
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.is_verify = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"
    
    
def test_login_user_not_active(client, session, user):
    """
    The test_login_user_not_active function tests that a user cannot login if they are not active.
        It does this by first creating a new user, then deactivating the account and attempting to login with the same credentials.
        If successful, it will return an HTTP 403 status code and display an error message.
    
    :param client: Make requests to the flask application
    :param session: Access the database and make changes to it
    :param user: Get the user from the database
    :return: A 403 status code and the user_not_active message
    """
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.is_active = False
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    USER_NOT_ACTIVE
    assert response.status_code == 403, response.text
    data = response.json()
    assert data["detail"] == USER_NOT_ACTIVE


def test_login_wrong_password(client, session, user):
    """
    The test_login_wrong_password function tests the login endpoint with a wrong password.
    It first creates a user and activates it, then tries to log in with the wrong password.
    The response should be 401 Unauthorized.
    
    :param client: Make requests to the application
    :param session: Create a new user in the database
    :param user: Pass the user data to the test function
    :return: A 401 status code and the invalid_password message
    """
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.is_active = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": 'password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == INVALID_PASSWORD


def test_login_wrong_email(client, user):
    """
    The test_login_wrong_email function tests the login endpoint with a wrong email.
    It should return an HTTP 401 status code and a JSON response containing the detail message: &quot;Invalid email or password.&quot;
    
    
    :param client: Make requests to the application
    :param user: Create a user in the database, so that we can use it to test our login functionality
    :return: 401 status code and the detail of the error message
    """
    response = client.post(
        "/api/auth/login",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == INVALID_EMAIL
