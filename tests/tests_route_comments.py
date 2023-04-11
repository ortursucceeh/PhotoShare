import json
from unittest.mock import MagicMock, patch

import pytest
import unittest

from src.database.models import User, Comment, Post
from src.services.auth import auth_service


@pytest.fixture()
def token(client, user, session, monkeypatch):
    """
    The token function is used to create a token for the user.
        It takes in four arguments: client, user, session and monkeypatch.
        The function first mocks the send_email function from src/routes/auth.py file using monkeypatching technique
        and then creates a new user by posting to /api/auth/signup endpoint with json data as argument which contains
        email and password of the new user. Then it fetches that newly created current_user from database using session object
        provided by pytest-flask plugin (which is an instance of SQLAl

    :param client: Make requests to the api
    :param user: Create a user in the database
    :param session: Access the database
    :param monkeypatch: Mock the send_email function
    :return: The token of the user

    """
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.is_verify = True
    session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope="module")
def fix_comment():

    """
    The fix_comment function takes a comment dictionary and returns the same comment with updated_at set to None.
        Args:
            comment (dict): A dictionary representing a single Comment object.

    :return: A dictionary
    :doc-author: Trelent
    """
    comment = {
        "text": "Test text for new comment",
        "id": 1,
        "created_at": "2023-04-09T22:50:03.062Z",
        "updated_at": None,
        "user_id": 1,
        "post_id": 1,
        "update_status": False
    }
    return comment


def test_create_comment(client, token):
    """
    The test_create_comment function tests the creation of a new comment.
        The function uses the client fixture to make a POST request to the /api/comments/new/&lt;post_id&gt; endpoint,
        passing in an Authorization header with a valid JWT token and JSON data containing text for the new comment.
        The response is then checked for status code 200 OK and that it contains all expected fields.

    :param client: Make requests to the api
    :param token: Make sure that the user is logged in and has access to the comment
    :return: A status code of 200 and the following data:
    :doc-author: Trelent
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.post(
        "api/comments/new/1", json={"text": "Test text for new comment"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text

    body_data = response.json()
    assert body_data == {
        "text": "Test text for new comment",
        "id": 1,
        "created_at": f"{body_data['created_at']}",
        "updated_at": None,
        "user_id": 1,
        "post_id": 1,
        "update_status": False
    }


def test_edit_comment(client, session, token, user):
    """
    The test_edit_comment function tests the edit_comment function in the comments.py file.
    It does this by first creating a comment, then editing that comment and checking to see if it was edited correctly.

    :param client: Make requests to the api
    :param session: Create a database session for the test
    :param token: Authenticate the user
    :param user: Create a user in the database
    :return: The status code 200
    :doc-author: Trelent
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.put(
        "api/comments/edit/1", json={"text": "NEW Test text for new comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_delete_comment(client, session, token):
    """
    The test_delete_comment function tests the delete_comment function in the comments.py file.
    It does this by first creating a comment, then deleting it.

    :param client: Make requests to the api
    :param session: Create a new session for the test
    :param token: Authenticate the user
    :return: A 200 status code
    :doc-author: Trelent
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.put(
        "api/comments/edit/1", json={"text": "NEW Test text for new comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_create_comment_2(client, token):
    """
    The test_create_comment_2 function tests the creation of a new comment.
        The test_create_comment_2 function is similar to the test_create_comment function, but it uses a different token.
        This token has been created with an email that does not exist in our database, so we expect to get an error message.

    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: 200
    :doc-author: Trelent
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.post(
        "api/comments/new/1", json={"text": "Test text for new comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_get_single_comm(client, session, token):
    """
    The test_get_single_comm function tests the GET /api/comments/single/&lt;int:comment_id&gt; endpoint.
        It does so by first creating a comment, then making a request to the endpoint with that comment's id.
        The response is checked for status code 200 and content-type application/json.
    :param client: Send a request to the api
    :param session: Create a session for the test to run in
    :param token: Authenticate the user and allow access to the api
    :return: A 200 status code and a json object
    :doc-author: Trelent
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.get("api/comments/single/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text


def test_comment_by_auth(client, session, token):
    """
    The test_comment_by_auth function tests the /api/comments/by_author endpoint.
    It does so by first creating a client, session, and token for use in the test.
    Then it uses that client to make a GET request to the /api/comments/by_author endpoint with an Authorization header containing our token.
    The response is then checked for status code 200 (OK) and if not found, we print out what went wrong.

    :param client: Make requests to the flask app
    :param session: Create a new session
    :param token: Authenticate the user
    :return: A 200 status code
    :doc-author: Trelent
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.get(
        "api/comments/by_author/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_comm_post_auth(client, session, token):
    """
    The test_comm_post_auth function tests the /api/comments/post_by_author endpoint.
        It does so by first creating a mock token, and then using that token to make a request to the
        /api/comments/post_by_author endpoint with an author id of 1 and post id of 1. The function then asserts that
        the response status code is 200.

    :param client: Make requests to the flask app
    :param session: Create a database session for the test
    :param token: Authenticate the user
    :return: The comments posted by a specific author

    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.get(
        "api/comments/post_by_author/1/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
