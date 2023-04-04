import sys
import os
from unittest.mock import MagicMock

from src.database.models import User
from src.conf.messages import ALREADY_EXISTS, EMAIL_NOT_CONFIRMED, INVALID_PASSWORD, INVALID_EMAIL

sys.path.append(os.getcwd())


def test_create_user(client, user, monkeypatch):
    """
    The test_create_user function tests the /api/auth/signup endpoint.
    It does so by creating a user and then checking that the response is 201 (created)
    and that the email address of the created user matches what was sent in.

    :param client: Send requests to the api
    :param user: Pass in the user data to create a new user
    :param monkeypatch: Mock the confirmed_email function
    :return: A 201 status code, which means that the user was created
    :doc-author: Trelent
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

    :param client: Make requests to the api
    :param user: Create a user in the database
    :return: A 409 status code and a message that the user already exists
    :doc-author: Trelent
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
    The test_login_user_not_confirmed function tests that a user cannot login if they have not confirmed their
    email address.
    The test_login_user_not_confirmed function takes two arguments: client and user. The client argument is the
    Flask test
    client, which allows us to make requests to our application without running the server. The user argument
    is a fixture that returns a dictionary of data for an unconfirmed User object.

    :param client: Make requests to the api
    :param user: Get the user data from the fixture
    :return: A 401 status code and a message saying that the email is not confirmed
    :doc-author: Trelent
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
    The test_login_user function tests the login endpoint.
    It does this by first creating a user, then confirming that user's account.
    Then it sends a POST request to the /api/auth/login endpoint with the email and password of that user as data in
    JSON format.
    The response is checked for status code 200 (OK) and then its JSON content is checked for
    token_type &quot;bearer&quot;.

    :param client: Create a test client for the flask application
    :param session: Create a new user in the database
    :param user: Pass the user fixture into the test function
    :return: The token_type as &quot;bearer&quot;
    :doc-author: Trelent
    """
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, user):
    """
    The test_login_wrong_password function tests the login endpoint with a wrong password.
        It should return a 401 status code and an error message.

    :param client: Make requests to the api
    :param user: Pass the user data to the function
    :return: The status code 401 and the message &quot;invalid password&quot;
    :doc-author: Trelent
    """

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
    It should return a 401 status code and an error message.

    :param client: Make requests to the app
    :param user: Create a user in the database
    :return: A 401 status code and a message
    :doc-author: Trelent
    """
    response = client.post(
        "/api/auth/login",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == INVALID_EMAIL
