# import requests
# from fastapi import Request, UploadFile
# from requests_toolbelt.multipart.encoder import MultipartEncoder

from datetime import datetime
from unittest.mock import MagicMock, patch
import io
from PIL import Image
import pytest
from src.database.models import User, Post
from src.services.auth import auth_service
from src.conf.messages import NOT_FOUND


@pytest.fixture()
def token(client, user, session, monkeypatch):
    """
    The token function is used to create a user, verify the user, and then log in as that user.
    It returns an access token for use in other tests.
    
    :param client: Make requests to the api
    :param user: Create a user in the database
    :param session: Create a new session
    :param monkeypatch: Mock the send_email function
    :return: The access_token from the response
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


@pytest.fixture()
def post(user, token, session):
    """
    The post function creates a new post in the database.
        It takes three arguments: user, token, and session.
        The function first queries the User table for an existing user with the email address provided by 'user'.
        If no such user exists, it returns None. Otherwise it queries Post for an existing post with that same id as cur_user's id. 
        If no such post exists, then a new one is created using information from 'user' and added to Post.
    
    :param user: Get the user_id of the current user
    :param token: Check if the user is authenticated
    :param session: Query the database
    :return: A post object
    """
    cur_user = session.query(User).filter(User.email == user['email']).first()
    post = session.query(Post).first()
    if post is None:
        post = Post(
            image_url="https://res.cloudinary.com/dybgf2pue/image/upload/c_fill,h_250,w_250/Dominic",
            title="cat",
            descr="pet",
            created_at=datetime.now(),
            user_id=cur_user.id,
            public_id="Dominic",
            done=True
        )
        session.add(post)
        session.commit()
        session.refresh(post)
    return post


def test_create_post(client, token):
    """
    The test_create_post function tests the creation of a new post.
    It does so by first mocking the redis_cache object, which is used to store user tokens. 
    The mock returns None when called, which means that there is no token stored in redis_cache for this particular test case. 
    This allows us to create a new post without having to worry about whether or not we have an existing token stored in our cache. 
    We then create a file-like object (BytesIO) and use it as our image data for the POST request we make with requests library's client fixture function (client). We also pass along
    
    :param client: Make requests to the flask app
    :param token: Authenticate the user
    :return: The response
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None 
        file_data = io.BytesIO()
        image = Image.new('RGB', size=(100, 100), color=(255, 0, 0))
        image.save(file_data, 'jpeg')
        file_data.seek(0)
        data = {
            "title": "test_post",
            "descr": "test_post",
            "hashtags": ["test_post"]
            }
        
        response = client.post(
            "/api/posts/new/",
            headers={"Authorization": f"Bearer {token}"},
            data=data,
            files={"file": ("test.jpg", file_data, "image/jpeg")}
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["title"] == "test_post"
        assert data["descr"] == "test_post"
        assert data["image_url"] != None
        assert "id" in data


def test_get_post(post, client, token):
    """
    The test_get_post function tests the get_post function in the posts.py file.
    It does this by creating a post, then using that post to test if it can be retrieved from the database.
    
    :param post: Create a post object for the test
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A response object
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/by_id/{post.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "test_post"
        assert "id" in data


def test_get_post_not_found(post, client, token):
    """
    The test_get_post_not_found function tests the get_post function in the posts.py file.
    It does this by first patching the redis_cache object from auth_service with a mock object,
    and then setting that mock's return value to None (which is what it would be if there was no post).
    Then, we make a GET request to /api/posts/by_id/{post.id+2} (where post is an instance of Post), and check that 
    the response status code is 404 and that data[&quot;detail&quot;] == NOT FOUND.
    
    :param post: Pass in the post fixture
    :param client: Send a request to the server
    :param token: Authenticate the user
    :return: 404, but the code returns 200
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/by_id/{post.id+1}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_get_post_by_title(post, client, token):
    """
    The test_get_post_by_title function tests the get_post_by_title endpoint.
        It does so by first creating a post, then using the client to make a GET request to /api/posts/by_title/{post.title}.
        The response is checked for status code 200 and that it contains data with title, descr, and image url.
    
    :param post: Create a post in the database before the test is run
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: The post title, description and image url
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/by_title/{post.title}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["title"] == "test_post"
        assert data[0]["descr"] == "test_post"
        assert data[0]["image_url"] != None


def test_get_post_by_title_not_found(client, token):
    """
    The test_get_post_by_title_not_found function tests the get_post_by_title endpoint.
    It does so by mocking the redis cache and returning None when it is called.
    The test then makes a request to the endpoint with a title that doesn't exist in our database, 
    and asserts that we receive a 404 response.
    
    :param client: Make requests to the api
    :param token: Pass the token to the function
    :return: A 404 error
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/posts/by_title/other_test",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_get_posts(client, token):
    """
    The test_get_posts function tests the /api/posts/all endpoint.
    It does so by first mocking out the redis_cache object in auth_service, and then setting its get method to return None.
    This is done because we want to test that our code will work if there is no cache available (i.e., a new user).
    Then, we make a GET request to /api/posts/all with an Authorization header containing our token from above. 
    We assert that this returns 200 OK and contains at least one post.
    
    :param client: Make requests to the api
    :param token: Pass in the token that is generated by the test_login function
    :return: A list of posts
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/posts/all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


def test_update_post(post, client, token):
    """
    The test_update_post function tests the update_post function in the posts.py file.
    It does this by creating a post, then using a client to make an HTTP PUT request to 
    the /api/posts/{post.id} endpoint with json data containing title, descr and hashtags keys 
    and values of &quot;other_post&quot;. It also includes an Authorization header with a Bearer token value. 
    The test asserts that the response status code is 200 and that it contains json data with title, descr and id keys.
    
    :param post: Pass the post object to the function
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A 200 status code
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/posts/{post.id}",
            json={
                "title": "other_post",
                "descr": "other_post",
                "hashtags": ["other_post"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "other_post"
        assert data["descr"] == "other_post"
        assert "id" in data


def test_update_post_not_found(post, client, token):
    """
    The test_update_post_not_found function tests the update_post function in the posts.py file.
    It does this by creating a post, then using client to make a PUT request to /api/posts/{post.id+2} with json data and an Authorization header containing token as its value, which is returned from auth_service's redis_cache object's get method (which returns None).
    The response status code should be 404 and its text should be NOT FOUND.
    
    :param post: Create a post object to be used in the test
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A 404 status code and the not_found message
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/posts/{post.id+1}",
            json={
                "title": "other_post",
                "descr": "other_post",
                "hashtags": ["other_post"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_delete_post(post, client, token):
    """
    The test_delete_post function tests the delete_post function in the posts.py file.
    It does this by creating a post, then deleting it using the client and token that were passed into it as arguments.
    
    :param post: Create a post in the database
    :param client: Make requests to the api
    :param token: Pass the token to the test_delete_post function
    :return: A response object
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/posts/{post.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "other_post"
        assert data["descr"] == "other_post"
        assert "id" in data


def test_repeat_delete_post(post, client, token):
    """
    The test_repeat_delete_post function tests that a user cannot delete the same post twice.
        It does this by first deleting a post, then attempting to delete it again.
        The second attempt should fail with an HTTP 404 error.
    
    :param post: Pass the post object to the function
    :param client: Make requests to the api
    :param token: Pass the token to the function
    :return: A 404 error code
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/posts/{post.id-1}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND
        