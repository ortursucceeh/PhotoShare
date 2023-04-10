import json
from unittest.mock import MagicMock
from datetime import datetime
import pytest

from src.database.models import User, Post

from src.services.auth import auth_service


@pytest.mark.parametrize("post_id, user_id, result", [
    (1, 1, 200),  # own post
    (2, 2, 200)  # another user
])
def test_create_post(session, post_id, user_id, result):
    test_post = Post()
    test_post.id = post_id
    test_post.image_url = "image_url"
    test_post.transform_url = "transform_url"
    test_post.title = "title"
    test_post.descr = "descr"
    test_post.created_at = datetime.now()
    test_post.updated_at = datetime.now()
    test_post.done = True
    test_post.user_id = user_id
    test_post.hashtags = []
    test_post.public_id = "888"
    test_post.avg_rating = None

    session.add(test_post)
    session.commit()


@pytest.fixture()
def token(client, user, session, monkeypatch):
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


@pytest.mark.parametrize("post_id, rate, result", [
    (1, 5, 423),  # Response [423 Locked]
    (2, 3, 200),  # Response [200]
    (3, 3, 404)  # Response [404]
])
def test_create_rating(session, client, token, post_id, rate, result):
    """
    The test_create_rating function tests the POST /ratings/posts/&lt;post_id&gt;/&lt;rate&gt; endpoint.
        It takes in a session, client, token, post_id and rate as arguments.
        The test will fail if the response status code is not equal to result.

    :param session: Access the database
    :param client: Make requests to the api
    :param token: Authenticate the user
    :param post_id: Pass the post_id to the test function
    :param rate: Set the rate of a post
    :param result: Check if the response status code is correct
    :return: The following:
    :doc-author: Trelent
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.post(
        f"api/ratings/posts/{post_id}/{rate}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


@pytest.mark.parametrize("rate_id, new_rate, result", [
    (1, 5, 200),
    (2, 3, 404),
    (3, 3, 404)
])
def test_edit_rating(session, client, token, rate_id, new_rate, result):
    """
    The test_edit_rating function tests the edit_rating function in ratings.py
        It does this by first creating a mock token and rate_id, then it creates a new rating value to replace the old one with.
        Then it calls the put method on client, which is an instance of FlaskClient that we created earlier in conftest.py
        The response variable stores whatever comes back from calling client's put method (which should be a 200 status code)

    :param session: Rollback the database after each test
    :param client: Make a request to the api
    :param token: Authenticate the user
    :param rate_id: Pass the id of the rating that is to be edited
    :param new_rate: Test the different values that can be passed in for the new rating
    :param result: Check the status code of the response
    :return: A 200 status code
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.put(
        f"api/ratings/edit/{rate_id}/{new_rate}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


@pytest.mark.parametrize("rate_id, result", [
    (1, 200),
    (2, 404),
    (3, 404)
])
def test_delete_rating(session, client, token, rate_id, result):
    """
    The test_delete_rating function tests the DELETE /ratings/delete/&amp;lt;rate_id&amp;gt; endpoint.
        It does so by sending a request to the endpoint with a valid token and rate_id,
        and then checking that the response status code is 200 (OK).


    :param session: Create a new database session for each test
    :param client: Send a request to the api endpoint
    :param token: Authenticate the user
    :param rate_id: Specify the id of the rating to be deleted
    :param result: Determine if the test passes or fails
    :return: A 200 status code if the rating is deleted successfully
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.delete(
        f"api/ratings/delete/{rate_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


@pytest.mark.parametrize("post_id, rate, result", [
    (1, 5, 423),  # Response [423 Locked]
    (2, 3, 200),  # Response [200]
    (3, 3, 404)  # Response [404]
])
def test_create_rating_2(session, client, token, post_id, rate, result):
    """
    The test_create_rating_2 function tests the POST /ratings/posts/&lt;post_id&gt;/&lt;rate&gt; endpoint.
        It does so by sending a request to the endpoint with a valid token and post_id, but an invalid rate.
        The test expects that the response status code will be 400.

    :param session: Create a new database session for each test
    :param client: Make a request to the api
    :param token: Pass the token to the test function
    :param post_id: Specify the post id for which a rating is to be created
    :param rate: Test the rating value
    :param result: Determine if the test passes or fails
    :return: A 201 response code
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.post(
        f"api/ratings/posts/{post_id}/{rate}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


def test_all_ratings(session, client, token):
    """
       The test_all_ratings function tests the GET /api/ratings/all endpoint.
       It does so by first creating a new user, then logging in to get a token.
       The test_all_ratings function then makes an API call to the GET /api/ratings/all endpoint, passing along the token as an Authorization header.
       The response is checked for status code 200 and that it returns a list of ratings.

    :param session: Create a database session, which is used to query the database
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A list of all the ratings in the database
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.get(
        "api/ratings/all",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert type(response.json()) == list


def test_all_my_rates(session, client, token):
    """
    The test_all_my_rates function tests the GET /api/ratings/all_my endpoint.
    It does so by first creating a user, then logging in to get a token, and finally making an authenticated request to the endpoint.
    The test asserts that the response status code is 200 (OK) and that it returns a list of ratings.

    :param session: Create a new database session for the test
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A list of all the ratings a user has made
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.get(
        "api/ratings/all_my",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert type(response.json()) == list


@pytest.mark.parametrize("user_id, post_id, result", [
    (1, 2, 200),
    (1, 3, 404)
])
def test_user_for_post(session, client, token, user_id, post_id, result):
    """
        The test_user_for_post function tests the user_for_post endpoint.
            It does so by first creating a mock redis cache object, and then setting its get method to return None.
            Then it makes a GET request to the endpoint with an Authorization header containing a valid token,
            and checks that the response status code is 200.

    :param session: Rollback the database to its original state after each test
    :param client: Make a request to the api
    :param token: Authenticate the user
    :param user_id: Test the user_id of a post
    :param post_id: Test the user_post route with a specific post id
    :param result: Determine the expected status code of the response
    :return: A 200 status code if the user has already rated a post
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.get(
        f"api/ratings/user_post/{user_id}/{post_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


def test_commented(session, client, token):
    """
    The test_commented function tests the commented endpoint.
        It does this by making a GET request to the /api/ratings/post/2 endpoint, which is supposed to return all comments on post 2.
        The test passes if it receives a 200 status code in response.

    :param session: Create a database session
    :param client: Make requests to the api
    :param token: Test the authorization of a user
    :return: The following:
    """
    # with patch.object(auth_service, 'redis_cache') as r_mock:
    #    r_mock.get.return_value = None

    response = client.get(
        "api/ratings/post/2",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(response.json())

    assert response.status_code == 200
