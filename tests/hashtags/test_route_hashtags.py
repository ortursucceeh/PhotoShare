import pytest
from unittest.mock import MagicMock, patch

from src.database.models import User,  Hashtag
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
    :return: A token, which is then used in the test function
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
def tag(user, token, session):
    """
    The tag function takes in a user, token, and session.
    It then queries the database for the current user and hashtag.
    If there is no hashtag it creates one with a title of dog and adds it to the database.
    
    :param user: Get the user id from the database
    :param token: Authenticate the user
    :param session: Query the database
    :return: An object of type hashtag, which is a sqlalchemy model
    """
    cur_user = session.query(User).filter(User.email == user['email']).first()
    tag = session.query(Hashtag).first()
    if tag is None:
        tag = Hashtag(
            title="dog",
            user_id=cur_user.id
        )
        session.add(tag)
        session.commit()
        session.refresh(tag)
    return tag


@pytest.fixture()
def body():
    return {
        "title": "string"
    }



def test_create_tag(body, client, token):
    """
    The test_create_tag function tests the creation of a new hashtag.
    It does so by first mocking out the redis_cache object, which is used to cache data in our application. 
    The mock object is then set to return None when its get method is called, which will be done by our code when it tries to retrieve cached data from Redis. 
    This ensures that we are not using any cached data during this test and that we are testing against fresh database records each time.
    
    :param body: Pass the data to the endpoint
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A 200 status code, but i want it to return a 201 status code
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.post(f'/api/hashtags/new/', json=body,
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data.get('title') is not None


def test_read_my_tags(client, token):
    """
    The test_read_my_tags function tests the read_my_tags function in the hashtags.py file.
    It does this by mocking out the redis cache and returning None, which will cause a call to 
    the database for data. It then makes a GET request to /api/hashtags/my/, with an Authorization header containing 
    a valid token, and asserts that it returns 200 OK status code.
    
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A list of dictionaries
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(f'/api/hashtags/my/',
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["title"] == "string"
        assert "id" in data[0]


def test_read_all_tags(client, token):
    """
    The test_read_all_tags function tests the read_all_tags function in the hashtag.py file.
    It does this by mocking out the redis cache and then making a GET request to /api/hashtags/all/.
    The response is checked for a 200 status code, and then it is checked that data returned from 
    the API call is an instance of list, that one of its elements has a title attribute equal to &quot;string&quot;, 
    and that all elements have an id attribute.
    
    :param client: Make requests to the app
    :param token: Authenticate the user
    :return: A list of dictionaries
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(f'/api/hashtags/all/',
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["title"] == "string"
        assert "id" in data[0]


def test_read_tag_by_id(tag, client, token):
    """
    The test_read_tag_by_id function tests the read_tag_by_id function in the hashtag.py file.
    It does this by first creating a tag object, then using that tag to create a client and token for use in testing.
    The test then uses patching to mock out redis cache, which is used as part of the auth service's authentication process.
    
    :param tag: Pass in a tag object
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A 200 status code, but the test_read_tag function returns a 404
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(f'/api/hashtags/by_id/{tag.id}',
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "string"
        assert "id" in data


def test_read_tag_by_id_not_found(tag, client, token):
    """
    The test_read_tag_by_id_not_found function tests the read_tag_by_id function in the hashtag.py file.
    It does this by first creating a tag object, then it creates a client and token to be used for testing purposes.
    Then it uses patch to mock out redis cache so that we can test what happens when there is no data in redis cache. 
    The response variable stores the result of calling client's get method on /api/hashtags/by_id/{tag id + 1} with an authorization header containing our token as its value (this will return 404 because we are trying to access a tag that doesn't
    
    :param tag: Create a tag object to be used in the test
    :param client: Send a request to the server
    :param token: Authenticate the user
    :return: 404 and &quot;tag not found&quot;
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(f'/api/hashtags/by_id/{tag.id+1}',
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_update_tag(tag, client, token):
    """
    The test_update_tag function tests the update_tag function in the hashtags.py file.
    It does this by first creating a tag object, then using that to create a response from 
    the client's put request to /api/hashtags/upd_tag/{tag.id}. The test asserts that the 
    response status code is 200 and that data[&quot;title&quot;] == &quot;new_test_tag&quot;. It also asserts 
    that &quot;id&quot; is in data.
    
    :param tag: Pass in the tag object created by the fixture
    :param client: Make requests to the api
    :param token: Pass the token to the test function
    :return: The following:
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.put(f'/api/hashtags/upd_tag/{tag.id}',
                            json={"title": "new_test_tag"},
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "new_test_tag"
        assert "id" in data


def test_update_tag_not_found(tag, client, token):
    """
    The test_update_tag_not_found function tests the update_tag function in the api.py file.
    It does this by first patching the redis_cache object from auth_service with a mock object, 
    and then setting that mock's get method to return None (which is what it would do if there was no token). 
    Then, we make a PUT request to /api/hashtags/upd_tag/{id} with an id that doesn't exist in our database and check for 404 status code and &quot;Tag not found&quot; detail message.
    
    :param tag: Create a tag object that is used in the test
    :param client: Send the request to the api
    :param token: Authenticate the user
    :return: 404 status code, but the test fails
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.put(f'/api/hashtags/upd_tag/{tag.id+1}',
                            json={"title": "new_test_tag"},
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_delete(tag, client, token):
    """
    The test_delete function tests the DELETE /api/hashtags/del/{tag_id} endpoint.
    It does so by first creating a new tag, then deleting it and checking that the response is 200 OK.
    
    
    :param tag: Pass in a tag object for the test to use
    :param client: Make requests to the application
    :param token: Authenticate the user
    :return: The response
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(f"/api/hashtags/del/{tag.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "new_test_tag"
        assert "id" in data


def test_repeat_delete_tag(client, token):
    """
    The test_repeat_delete_tag function tests the repeat deletion of a hashtag.
        The test_repeat_delete_tag function is called by the pytest framework and passes in client, token as arguments.
        The test_repeat_delete_tag function uses patch to mock out auth service's redis cache with r mock. 
        r mock's get method returns None when called by the delete method on client which deletes a hashtag with id 1 from hashtags table in database using an HTTP DELETE request and headers containing Authorization header set to Bearer followed by token value passed into test case as argument. 
        Assertions are
    
    :param client: Make requests to the api
    :param token: Pass the token to the test function
    :return: 404 status code, but the code returns 200
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(f"/api/hashtags/del/{1}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND

