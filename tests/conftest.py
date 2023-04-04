import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database.models import Base
from src.database.connect_db import get_db

sys.path.append(os.getcwd())

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database

    """
    The session function is a fixture that will ensure that a new database is
    created for each test, and it will be torn down when the test ends. This
    allows you to have complete isolation between your tests. The session object
    is also scoped so that multiple tests can use it if they wish.

    :return: A function that returns a session
    :doc-author: Trelent
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    """
    The client function is a fixture that creates an instance of the TestClient class.
    The TestClient class allows you to make HTTP requests in your tests.
    It acts as a dummy Web browser, and each time you call one of its methods, such as get() or post(), it sends an
    HTTP request to your application and stores the response data for later inspection.

    :param session: Pass the test client a session object
    :return: A test client
    :doc-author: Trelent
    """
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    """
    The user function is used to create a new user.
    It takes no arguments and returns a dictionary with the following keys:
    username, email, password, role and avatar.

    :return: A dictionary with the user's details
    :doc-author: Trelent
    """
    return {
        "username": "deadpool",
        "email": "deadpool@example.com",
        "password": "123456789",
        'role': 'User',
        'avatar': 'URL-avatar'
        }
