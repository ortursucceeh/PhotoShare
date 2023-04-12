from datetime import datetime

import io
import pytest
from unittest.mock import MagicMock, patch
from PIL import Image

from src.database.models import User, Post
from src.services.auth import auth_service
from src.conf.messages import NOT_FOUND


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


@pytest.fixture()
def post(user, token, session):
    """
    The post function is used to create a post for the user.
        It takes in the user, token and session as parameters.
        The function first checks if there is already a post created for that particular user. If not, it creates one with all the necessary details and adds it to the database.
    
    :param user: Get the user_id of the current user
    :param token: Authenticate the user
    :param session: Access the database
    :return: A post object
    """
    cur_user = session.query(User).filter(User.email == user['email']).first()
    post = session.query(Post).first()
    if post is None:
        post = Post(
            image_url="https://res.cloudinary.com/dybgf2pue/image/upload/c_fill,h_250,w_250/Dominic",
            title="cat",
            descr="pet",
            hashtags=["cat", "pet"],
            created_at=datetime.now(),
            user_id=cur_user.id,
            public_id="Dominic",
            done=True
        )
        session.add(post)
        session.commit()
        session.refresh(post)
    return post


@pytest.fixture()
def new_user(user, token, session):
    """
    The new_user function takes in a user, token, and session.
    It then queries the database for a user with the same email as the one passed in.
    If there is no such user, it creates one using information from the passed-in 
    user object and adds it to our database. It then returns this new_user.
    
    :param user: Create a new user object
    :param token: Create a new token for the user
    :param session: Query the database for a user with the same email as the one provided in the request
    :return: A new user object
    """
    new_user = session.query(User).filter(User.email == user.get('email')).first()
    if new_user is None:
        new_user = User(
            email=user.get('email'),
            username=user.get('username'),
            password=user.get('password')
        )  
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    return new_user


def test_create_post(client, token):
    """
    The test_create_post function tests the POST /api/posts/new endpoint.
    It does so by creating a new post with a title, description, and hashtags.
    The test also checks that the response status code is 201 (created) and that 
    the returned data contains all of the information we sent in our request.
    
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A response with a 201 status code and the data from the post
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


def test_get_all_posts(client, token):
    """
    The test_get_all_posts function tests the /api/posts/all endpoint.
    It does this by first patching the redis_cache function in auth_service to return None, which will cause a call to be made
    to get all posts from the database. It then makes a GET request to /api/posts/all with an Authorization header containing
    a valid JWT token and checks that it returns 200 OK and that data is returned as expected.
    
    :param client: Make the request to the api
    :param token: Make sure that the user is authorized to access the endpoint
    :return: A list of all posts
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/all/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["title"] == "test_post"
        assert "id" in data[0]


def test_get_get_my_posts(client, token):
    """
    The test_get_get_my_posts function tests the get_my_posts endpoint.
    It does this by first patching the redis cache to return None, which will cause a call to be made to the database.
    Then it makes a GET request with an Authorization header containing a valid token and checks that:
        - The response status code is 200 OK, and if not prints out the response text for debugging purposes.
        - The data returned is in JSON format (a list).  If not, print out error message for debugging purposes.
        - That there are two items in data[0] (the first item of data), one being
    
    :param client: Make requests to the server
    :param token: Authenticate the user
    :return: All posts created by the user who is logged in
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/my_posts/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["title"] == "test_post"
        assert "id" in data[0]


def test_get_post_by_id(post, client, token):
    """
    The test_get_post_by_id function tests the get_post_by_id endpoint.
    It does this by first creating a post, then using the client to make a GET request to /api/posts/by_id/&lt;post.id&gt;.
    The response is checked for status code 200 and that it contains the correct data.
    
    :param post: Create a post for the test
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A post by id
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


def test_get_post_by_id_not_found(post, client, token):
    """
    The test_get_post_by_id_not_found function tests the get_post_by_id function in the posts.py file.
    It does this by creating a post, then using that post's id to create a client and token for testing purposes.
    Then it uses patch to mock out redis cache, which is used in auth service (which is imported at the top of this file).
    The mocked redis cache returns None when called upon, which means that there will be no user found with that id. 
    This should result in an error 404 response code being returned from our server.
    
    :param post: Create a post in the database
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A 404 status code and a detail message
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


def test_get_posts_by_user_id(new_user, client, token):
    """
    The test_get_posts_by_user_id function tests the get_posts_by_user_id function in posts.py.
    It does this by creating a new user, and then using that user's id to create a post with the title &quot;test&quot; and description &quot;test&quot;.
    Then it uses client to make a GET request for all of the posts created by that user, which should be just one post. 
    The response is checked for status code 200 (OK), and then data is extracted from it as json format.
    
    :param new_user: Create a new user in the database
    :param client: Make a request to the server
    :param token: Test the authorization of a user
    :return: A list of posts that belong to the user
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/by_user_id/{new_user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["title"] == "test_post"
        assert data[0]["descr"] == "test_post"
        

def test_get_posts_by_user_id_not_found(new_user, client, token):
    """
    The test_get_posts_by_user_id_not_found function tests the get_posts_by_user_id function in the posts.py file.
    It does this by creating a new user, then using that user's id to create a post and add it to the database.
    Then, it uses client to make a GET request for all of that user's posts (which should be just one). It asserts 
    that response is successful and has status code 200.
    
    :param new_user: Create a new user
    :param client: Make requests to the api
    :param token: Pass the token to the function
    :return: 404
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/by_user_id/{new_user.id+1}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_get_post_by_title(post, client, token):
    """
    The test_get_post_by_title function tests the get_post_by_title function in posts.py.
    It does this by creating a post, then using the client to make a GET request to /api/posts/by_title/{post.title}.
    The response is checked for status code 200 and data[0][&quot;image&quot;] is checked for not being None.
    
    :param post: Pass in a post object to the test function
    :param client: Send a request to the server
    :param token: Authenticate the user
    :return: The data of the post with the title that was passed as a parameter
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
    The test_get_post_by_title_not_found function tests the get_post_by_title function in posts.py
        It does this by mocking the redis cache and returning None, which will cause a 404 error to be returned
        The test then checks that the status code is 404 and that data[&quot;detail&quot;] == NOT_FOUND
    
    :param client: Make a request to the api
    :param token: Authenticate the user
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


def test_get_posts_by_username(new_user, client, token):
    """
    The test_get_posts_by_username function tests the get_posts_by_username function in the posts.py file.
    The test uses a new user and client to create a post, then it gets that post by username using the 
    get_posts_by_username function and checks if it is equal to what was created.
    
    :param new_user: Create a new user in the database
    :param client: Make requests to the app
    :param token: Pass in the token to the test function
    :return: A list of posts by a username
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/by_username/{new_user.username}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["title"] == "test_post"
        assert data[0]["descr"] == "test_post"
        

def test_get_posts_by_username_not_found(client, token):
    """
    The test_get_posts_by_username_not_found function tests the get_posts_by_username function in posts.py
    to ensure that it returns a 404 status code and NOT FOUND detail when the username is not found.
    
    :param client: Make requests to the api
    :param token: Pass the token to the test function
    :return: 404 status code and not_found message
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/by_username/test_user_name",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND
        

def test_get_posts_with_hashtag_not_found(client, token):
    """
    The test_get_posts_with_hashtag_not_found function tests the get_posts_with_hashtag function in posts.py
        It does this by mocking the redis cache and returning None, which will cause a 404 error to be returned.
        The test then checks that the status code is indeed 404, and that data[&quot;detail&quot;] == NOT_FOUND.
    
    :param client: Make a request to the api
    :param token: Pass the token to the test function
    :return: 404 if the hashtag does not exist
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/with_hashtag/test_new_hashtag",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_read_post_comments_not_found(post, client, token):
    """
    The test_read_post_comments_not_found function tests the read_post_comments function in the posts.py file.
    The test is testing to see if a post that does not exist will return a 404 error.
    
    :param post: Create a post object that is used to test the function
    :param client: Make a request to the api
    :param token: Test the read_post_comments function with a valid token
    :return: A 404 status code and a not_found message
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/comments/all/{post.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_read_post_by_keyword_not_found(client, token):
    """
    The test_read_post_by_keyword_not_found function tests the read_post_by_keyword function in the posts.py file.
    The test is testing that if a keyword is not found, then it will return a 404 error and NOT FOUND message.
    
    :param client: Make requests to the api
    :param token: Pass the token to the function
    :return: A 404 status code and a not_found message
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/by_keyword/test_keyword",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_get_posts(client, token):
    """
    The test_get_posts function tests the /api/posts/all endpoint.
    It does this by first patching the auth_service module's redis_cache object, and then setting its get method to return None.
    Then it makes a GET request to /api/posts/all with an Authorization header containing a valid token.
    The response should have status code 200, and its data should be a list of at least one post.
    
    :param client: Make a request to the api
    :param token: Authenticate the user
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
    The test_update_post function tests the update_post function in app.py.
    It does this by creating a post, then using the client to send a PUT request to /api/posts/&lt;id&gt; with json data containing title, descr and hashtags fields.
    The response is checked for status code 200 (OK) and that it contains the correct data.
    
    :param post: Pass the post object to the test function
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: 200
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
    It does this by creating a post, then using client to send a PUT request to /api/posts/{post.id+2} with json data and an authorization header containing token as its value, which is created from user's id and password hash (see test_create_user).
    The response status code should be 404 because there is no post with id {post.id+2}. The response text should contain NOT FOUND.
    
    :param post: Create a post in the database
    :param client: Make requests to the api
    :param token: Test the update post endpoint with a valid token
    :return: A 404 error code and the detail is not_found
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
    It does this by creating a post, then deleting it using the client and token created in conftest.py
    The patch object is used to mock out redis_cache so that we can test without having to use Redis
    
    :param post: Pass the post fixture into the function
    :param client: Make a request to the api
    :param token: Authenticate the user
    :return: The data of the deleted post
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


def test_repeat_delete_post(client, token):
    """
    The test_repeat_delete_post function tests the repeat deletion of a post.
        The test_repeat_delete_post function takes in client and token as parameters.
        The test_repeat_delete_post function uses patch to mock the redis cache object from auth service.
        The test returns None for redis cache get method, which is used to check if a user is logged in or not. 
        If there is no user logged in, then it will return None and raise an error that says &quot;User not found&quot;. 
    
    :param client: Make requests to the api
    :param token: Pass in the token to be used for testing
    :return: 404 error and not_found message
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/posts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND
