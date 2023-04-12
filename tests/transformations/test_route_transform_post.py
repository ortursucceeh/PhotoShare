from datetime import datetime
from unittest.mock import MagicMock, patch

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
    :param session: Access the database
    :param monkeypatch: Mock the send_email function
    :return: A token, which is used to test the protected endpoints
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
def post_id(user, token, session):
    """
    The post_id function takes in a user, token, and session.
    It then queries the database for the first post. If there is no post it creates one with default values.
    The function returns the id of that post.
    
    :param user: Get the user from the database
    :param token: Check if the user is logged in
    :param session: Query the database
    :return: The id of the post
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
    return post.id


@pytest.fixture()
def body():
    return {
        "circle": {
            "use_filter": True,
            "height": 400,
            "width": 400
        },
        "effect": {
            "use_filter": False,
            "art_audrey": False,
            "art_zorro": False,
            "cartoonify": False,
            "blur": False
        },
        "resize": {
            "use_filter": True,
            "crop": True,
            "fill": False,
            "height": 400,
            "width": 400
        },
        "text": {
            "use_filter": False,
            "font_size": 70,
            "text": ""
        },
        "rotate": {
            "use_filter": True,
            "width": 400,
            "degree": 45
        }
    }



def test_transform_metod(client, post_id, body, token):
    """
    The test_transform_metod function tests the transform_metod function in the transformations.py file.
    It does this by patching the redis_cache object from auth_service and setting its get method to return None,
    then it sends a PATCH request to /api/transformations/{post_id} with a json body containing an image url and 
    a token as headers, then it asserts that response status code is 200 (OK) and that data['transform_url'] is not None.
    
    :param client: Create a test client for the flask app
    :param post_id: Get the post id from the url
    :param body: Pass the json data to the endpoint
    :param token: Get the token from the fixture
    :return: None
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.patch(f'/api/transformations/{post_id}', json=body,
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data.get('transform_url') is not None


def test_transform_metod_not_found(client, post_id, body, token):
    """
    The test_transform_metod_not_found function tests the following:
        1. The response status code is 404 (Not Found)
        2. The response body contains a detail key with value NOT_FOUND
    
    :param client: Make requests to the api
    :param post_id: Create a post_id+2
    :param body: Pass the body of the request to be sent
    :param token: Pass the token to the test function
    :return: 404, but the correct answer is 200
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.patch(f'/api/transformations/{post_id+1}', json=body,
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_show_qr(client, post_id, user, token):
    """
    The test_show_qr function tests the show_qr function in transformations.py
    by mocking the redis cache and checking that a 200 response is returned with 
    a string as data.
    
    :param client: Make a request to the api
    :param post_id: Pass the post_id to the test function
    :param user: Pass the user data to the function
    :param token: Authenticate the user
    :return: A string
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.post(f'/api/transformations/qr/{post_id}', json=user,
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, str)


def test_show_qr_not_found(client, post_id, user, token):
    """
    The test_show_qr_not_found function tests the show_qr function in transformations.py
        to ensure that it returns a 404 status code and an appropriate error message when 
        the post ID is not found in Redis.
    
    :param client: Make a request to the api
    :param post_id: Generate a random id for the post that is created in the database
    :param user: Create a user object that is passed in the request body
    :param token: Pass the token to the function
    :return: A 404 error
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.post(f'/api/transformations/qr/{post_id+1}', json=user,
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND
    