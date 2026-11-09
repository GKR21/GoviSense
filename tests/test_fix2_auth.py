import pytest
from fastapi import HTTPException
from govisense.api.routes.auth import login, LoginRequest, ensure_seed_users
from govisense.db.session import init_db
from unittest.mock import patch


@pytest.fixture(autouse=True)
def setup_users():
    init_db()
    ensure_seed_users()


def test_seed_user_bcrypt_login_success():
    # Valid seed officer account
    req = LoginRequest(
        email="nimal@agriculture.gov.lk",
        password="officer123",
        role="officer"
    )
    res = login(req)
    assert "access_token" in res
    assert res["user"]["email"] == "nimal@agriculture.gov.lk"
    assert res["user"]["role"] == "Officer"


def test_wrong_password_returns_401():
    req = LoginRequest(
        email="nimal@agriculture.gov.lk",
        password="wrong_password_test",
        role="officer"
    )
    with pytest.raises(HTTPException) as exc_info:
        login(req)
    assert exc_info.value.status_code == 401
    assert "Invalid credentials" in exc_info.value.detail


def test_non_existent_user_returns_401():
    req = LoginRequest(
        email="ghost.user@unknown.lk",
        password="password123",
        role="officer"
    )
    with pytest.raises(HTTPException) as exc_info:
        login(req)
    assert exc_info.value.status_code == 401


def test_no_prototype_fallback_bypass():
    # "prototype" used to be a dynamic bypass password for any email
    req = LoginRequest(
        email="unregistered_pilot@anuradhapura.lk",
        password="prototype",
        role="officer"
    )
    with pytest.raises(HTTPException) as exc_info:
        login(req)
    assert exc_info.value.status_code == 401


def test_failed_db_lookup_returns_401():
    req = LoginRequest(
        email="nimal@agriculture.gov.lk",
        password="officer123",
        role="officer"
    )
    with patch("govisense.api.routes.auth.get_session", side_effect=Exception("Database connection timeout")):
        with pytest.raises(HTTPException) as exc_info:
            login(req)
        assert exc_info.value.status_code == 401
        assert "Database lookup error" in exc_info.value.detail

