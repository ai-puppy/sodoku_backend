import pytest
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    authenticate_user,
)
from app.config import settings
from app.schemas import TokenData


class TestPasswordFunctions:
    """Test password hashing and verification functions."""

    def test_password_hashing(self):
        """Test password hashing creates different hashes for same password."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2  # Different salts should produce different hashes
        assert len(hash1) > 50  # Bcrypt hashes are long
        assert hash1.startswith("$2b$")  # Bcrypt format

    def test_password_verification_success(self):
        """Test successful password verification."""
        password = "testpassword123"
        hashed_password = get_password_hash(password)

        assert verify_password(password, hashed_password) is True

    def test_password_verification_failure(self):
        """Test failed password verification with wrong password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed_password = get_password_hash(password)

        assert verify_password(wrong_password, hashed_password) is False

    def test_verify_empty_password(self):
        """Test password verification with empty password."""
        hashed_password = get_password_hash("testpassword")

        assert verify_password("", hashed_password) is False


class TestTokenFunctions:
    """Test JWT token creation and verification functions."""

    def test_create_access_token_with_expiry(self):
        """Test token creation with custom expiration."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)

        token = create_access_token(data, expires_delta)

        # Decode token to verify contents
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["sub"] == "testuser"

        # Check expiration is set correctly (within 1 second tolerance)
        expected_exp = datetime.utcnow() + expires_delta
        actual_exp = datetime.utcfromtimestamp(payload["exp"])
        assert abs((expected_exp - actual_exp).total_seconds()) < 1

    def test_create_access_token_default_expiry(self):
        """Test token creation with default expiration."""
        data = {"sub": "testuser"}

        token = create_access_token(data)

        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        # Check default 15 minute expiration
        expected_exp = datetime.utcnow() + timedelta(minutes=15)
        actual_exp = datetime.utcfromtimestamp(payload["exp"])
        assert abs((expected_exp - actual_exp).total_seconds()) < 1

    def test_verify_token_success(self):
        """Test successful token verification."""
        username = "testuser"
        token = create_access_token({"sub": username})

        credentials_exception = HTTPException(status_code=401, detail="Invalid token")
        token_data = verify_token(token, credentials_exception)

        assert isinstance(token_data, TokenData)
        assert token_data.username == username

    def test_verify_token_invalid_token(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid.token.here"
        credentials_exception = HTTPException(status_code=401, detail="Invalid token")

        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token, credentials_exception)
        assert exc_info.value.status_code == 401

    def test_verify_token_no_subject(self):
        """Test token verification with token missing 'sub' field."""
        token = jwt.encode(
            {"user": "testuser"}, settings.secret_key, algorithm=settings.algorithm
        )
        credentials_exception = HTTPException(status_code=401, detail="Invalid token")

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token, credentials_exception)
        assert exc_info.value.status_code == 401

    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        expired_time = datetime.utcnow() - timedelta(minutes=1)
        token = jwt.encode(
            {"sub": "testuser", "exp": expired_time},
            settings.secret_key,
            algorithm=settings.algorithm,
        )

        credentials_exception = HTTPException(status_code=401, detail="Invalid token")

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token, credentials_exception)
        assert exc_info.value.status_code == 401


class TestAuthenticateUser:
    """Test user authentication function."""

    def test_authenticate_user_success(self, db_session, sample_user, sample_user_data):
        """Test successful user authentication."""
        result = authenticate_user(
            db_session, sample_user_data["username"], sample_user_data["password"]
        )

        assert result is not False
        assert result.id == sample_user.id
        assert result.username == sample_user.username

    def test_authenticate_user_wrong_password(
        self, db_session, sample_user, sample_user_data
    ):
        """Test authentication with wrong password."""
        result = authenticate_user(
            db_session, sample_user_data["username"], "wrongpassword"
        )

        assert result is False

    def test_authenticate_user_nonexistent_user(self, db_session):
        """Test authentication with non-existent username."""
        result = authenticate_user(db_session, "nonexistent", "password")

        assert result is False

    def test_authenticate_user_empty_credentials(self, db_session):
        """Test authentication with empty credentials."""
        result = authenticate_user(db_session, "", "")

        assert result is False
