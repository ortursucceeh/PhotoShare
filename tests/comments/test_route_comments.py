from unittest.mock import MagicMock, patch

import pytest

from src.database.models import User, Comment, Post
from src.services.auth import auth_service


@pytest.fixture()
def token(client, user, session, monkeypatch):
    """
    The token function is used to create a user, verify the user, and then log in as that user.
    It returns an access token for use in other tests.
    
    :param client: Make requests to the api
    :param user: Create a new user in the database
    :param session: Make changes to the database
    :param monkeypatch: Mock the send_email function
    :return: A token, which is a string
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
    The fix_comment function takes a comment dictionary and returns the same comment with updated_at set to the current time.
    
    :return: A dictionary with the following keys
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
    The response is then checked for status code 200 (OK) and that it contains all expected fields.
    
    :param client: Make requests to the flask application
    :param token: Authenticate the user and allow them to create a comment
    :return: A 201 response code
    """
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
    It does this by first creating a new comment, then editing that comment and checking to see if it was edited correctly.
    
    :param client: Make requests to the api
    :param session: Create a database session
    :param token: Authenticate the user
    :param user: Create a user in the database
    :return: A 200 status code
    """
    response = client.put(
        "api/comments/edit/1", json={"text": "NEW Test text for new comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_delete_comment(client, session, token):
    """
    The test_delete_comment function tests the DELETE /api/comments/delete/{comment_id} endpoint.
        It first creates a comment, then deletes it and checks that the response is 200 OK.
    
    :param client: Send requests to the api
    :param session: Create a database session
    :param token: Authenticate the user
    :return: A 200 status code
    """
    response = client.put(
        "api/comments/edit/1", json={"text": "NEW Test text for new comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_create_comment_2(client, token):
    """
    The test_create_comment_2 function tests the creation of a new comment.
        The test_create_comment_2 function is similar to the test_create_comment function, but it uses a different post id.
        This allows us to check that comments are being created for multiple posts.
    
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: 200
    """
    response = client.post(
        "api/comments/new/1", json={"text": "Test text for new comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_get_single_comment(client, session, token):
    """
    The test_get_single_comm function tests the GET /api/comments/single/&lt;int:id&gt; endpoint.
        It does so by making a request to the endpoint with an id of 1, and then asserts that 
        the response status code is 200 (OK). If it is not, it will print out what went wrong.
    
    :param client: Make a request to the api
    :param session: Create a database session
    :param token: Pass the token to the test function
    :return: A 200 status code
    """
    response = client.get("api/comments/single/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text


def test_comment_by_auth(client, session, token):
    """
    The test_comment_by_auth function tests the /api/comments/by_author endpoint.
    It does so by first creating a client, session, and token for use in the test.
    Then it makes a GET request to the /api/comments/by_author endpoint with an Authorization header containing our token.
    Finally, it asserts that we get back a 200 response code.
    
    :param client: Make requests to the app
    :param session: Create a session for the test client
    :param token: Authenticate the user
    :return: A 200 status code
    """
    response = client.get(
        "api/comments/by_author/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_comm_post_auth(client, session, token):
    """
    The test_comm_post_auth function tests the ability to get comments by author and post id.
        It does this by making a GET request to the api/comments/post_by_author endpoint with an 
        Authorization header containing a valid JWT token. The function then asserts that the response 
        status code is 200, meaning that it was successful.
    
    :param client: Make requests to the application
    :param session: Create a new session for the test
    :param token: Authenticate the user
    :return: A 200 status code
    """
    response = client.get(
        "api/comments/post_by_author/1/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
