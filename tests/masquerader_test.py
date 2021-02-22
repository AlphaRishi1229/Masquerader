"""File made only for different test cases."""
import os

from config import current_config
from main import app, change_engine, drop_engine
import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from starlette.testclient import TestClient

Base = declarative_base()


@pytest.fixture(scope="module")
def application():
    """Yiest TestClient from FastAPI.

    Yields:
        app[TestClient] -- Testing based application
    """
    # print("This is in masqtest",engines)
    # engines = cleanup_database
    # print("Any change?",new_engine)
    print("application called")
    yield TestClient(app)


@pytest.fixture(scope="session")
def cleanup_database():
    """Creates a mock database for testing purposes.

    Creates a mock database on server for testing and deletes once done.
    """
    print("cleanupdata called")
    username = os.environ.get("POSTGRES_USER", "fyndlocal")
    password = os.environ.get("POSTGRES_PASS", "fynd@123")
    postgres_host = os.environ.get("POSTGRES_HOST", "postgres")
    postgres_port = os.environ.get("POSTGRES_PORT_5432_TCP_PORT", 5432)
    postgres_db = os.environ.get("POSTGRES_DB", "mockdb")
    if not password:
        db_dict = {
            "username": username,
            "password": password,
            "host": postgres_host,
            "port": postgres_port,
            "db": postgres_db,
        }
        default_db_url = current_config.POSTGRES_NOPASS_DSN.format(**db_dict)
        print("if no pass", default_db_url)

    else:
        db_dict = {
            "username": username,
            "password": password,
            "host": postgres_host,
            "port": postgres_port,
            "db": postgres_db,
        }
        default_db_url = current_config.POSTGRES_PASS_DSN.format(**db_dict)

    engine = create_engine(default_db_url)
    conn = engine.connect()
    test_masqueraderdb_url = current_config.POSTGRES_TEST_DSN.format(**db_dict)
    db_name = test_masqueraderdb_url.split("/")[-1]

    try:
        conn.execution_options(isolation_level="AUTOCOMMIT").execute(
            f"CREATE DATABASE {db_name}"
        )
    except Exception as e:
        print("exception", e)

    rv = create_engine(test_masqueraderdb_url)
    yield rv


def test_read_main(cleanup_database, application):
    """To check if server is working."""
    change_engine(cleanup_database)
    response = application.get("/_healthz")
    assert response.status_code == 200
    assert response.json() == {"message": "Mock Server Working"}


def test_create_user(cleanup_database, application):
    """Test to create user exists in db."""
    change_engine(cleanup_database)
    Base.metadata.drop_all(cleanup_database)
    response = application.post(
        "/user/create/",
        json={
            "name": "test",
            "is_active": True,
            "is_admin": True,
            "password": "test123",
        },
    )
    expected_resp = {
        "name": "test",
        "is_active": True,
        "is_admin": True,
        "id": 1,
        "urls": [],
    }

    assert response.json() == expected_resp


def test_user_auth(cleanup_database, application):
    """To test user authentication."""
    change_engine(cleanup_database)
    response = application.get(
        "/user/auth/", headers={"Authorization": "Basic dGVzdDp0ZXN0MTIz"}
    )
    auth_response = {
        "name": "test",
        "is_active": True,
        "is_admin": True,
        "id": 1,
        "urls": [],
    }
    assert response.json() == auth_response


def test_user_incorrect_auth(cleanup_database, application):
    """Test if wrong user tries to login."""
    change_engine(cleanup_database)
    response = application.get(
        "/user/auth/",
        headers={"Authorization": "Basic YWxwaGEtcmlzaGk6UmlzaGl2Z0AxMjM="},
    )
    auth_response = {"detail": "User Not Authenticated"}
    assert response.json() == auth_response


def test_url_create(cleanup_database, application):
    """Test if url gets created by user."""
    change_engine(cleanup_database)
    body = '{"identifier":"test","request_type":"GET","url":"test/test1","response":{"hi":"test"},"headers":{},"status_code":0,"latency":0,"is_active":true}'  # noqa
    response = application.post(
        "/url/create/",
        body,
        headers={"Authorization": "Basic dGVzdDp0ZXN0MTIz"},
    )
    expected_resp = {
        "identifier": "test",
        "request_type": "GET",
        "url": "/test/test1",
        "response": '{"hi": "test"}',
        "payload": "",
        "headers": {},
        "status_code": 200,
        "latency": 0,
        "is_active": True,
        "inactive_response": None,
        "inactive_status_code": None,
        "created_by": 1,
    }
    assert response.json() == expected_resp


def test_update_url(cleanup_database, application):
    """Test if url gets updated by user."""
    change_engine(cleanup_database)
    body = '{"url_to_update":"/test/test1","status_code_of_old_url":200, "request_type_of_old_url":"GET", "response":{"response":"changed"}}'  # noqa
    response = application.post(
        "/url/update/",
        body,
        headers={"Authorization": "Basic dGVzdDp0ZXN0MTIz"},
    )
    expected_resp = ["response"]
    assert response.json() == expected_resp


def test_all_url(cleanup_database, application):
    """Test to check if all urls are visible."""
    change_engine(cleanup_database)
    response = application.get(
        "/url/mocked/", headers={"Authorization": "Basic dGVzdDp0ZXN0MTIz"}
    )
    expected_resp = {
        "Urls_mocked_by_user": [{"GET": "/test/test1"}],
        "Other_mocked_urls": [],
    }
    assert response.json() == expected_resp


def test_get_url(cleanup_database, application):
    """Test if get url gives the response."""
    change_engine(cleanup_database)
    response = application.get(
        "/test/test1",
        headers={
            "x-identifier-id": "test",
            "x-modify-response": '{"lol": "it works"}',
        },
    )
    expected_resp = {"response": "changed", "lol": "it works"}
    print(response.json())
    assert response.json() == expected_resp


def test_toggle_url(cleanup_database, application):
    """Test if url gets toggled by user."""
    change_engine(cleanup_database)
    body = '{"url": "/test/test1","status_code": 200, "request_type": "GET", "is_active": false}' # noqa
    response = application.post(
        "/url/toggle/",
        body,
        headers={"Authorization": "Basic dGVzdDp0ZXN0MTIz"},
    )
    expected_resp = {"/test/test1": False}
    assert response.json() == expected_resp


def test_delete_url(cleanup_database, application):
    """Test if url gets toggled by user."""
    change_engine(cleanup_database)
    body = '{"url": "test/test1","status_code": 200, "request_type": "GET"}'
    response = application.post(
        "/url/delete/",
        body,
        headers={"Authorization": "Basic dGVzdDp0ZXN0MTIz"},
    )
    expected_resp = {"url removed": "test/test1"}
    drop_engine(cleanup_database)
    assert response.json() == expected_resp
