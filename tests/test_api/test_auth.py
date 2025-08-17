from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from jose import jwt

from app.config import settings
from app.models import User


class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_user_success(self, client: TestClient, db_session):
        """Test successful user registration."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpassword123",
        }

        response = client.post("/auth/register", json=user_data)

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "created_at" in data
        assert "hashed_password" not in data  # Should not expose password

        # Verify user was created in database
        user = (
            db_session.query(User)
            .filter(User.username == user_data["username"])
            .first()
        )
        assert user is not None
        assert user.email == user_data["email"]

    def test_register_user_duplicate_username(
        self, client: TestClient, sample_user, sample_user_data
    ):
        """Test registration with duplicate username."""
        user_data = {
            "username": sample_user_data["username"],  # Already exists
            "email": "different@example.com",
            "password": "testpassword123",
        }

        response = client.post("/auth/register", json=user_data)

        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_register_user_duplicate_email(
        self, client: TestClient, sample_user, sample_user_data
    ):
        """Test registration with duplicate email."""
        user_data = {
            "username": "differentuser",
            "email": sample_user_data["email"],  # Already exists
            "password": "testpassword123",
        }

        response = client.post("/auth/register", json=user_data)

        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_user_invalid_email(self, client: TestClient):
        """Test registration with invalid email format."""
        user_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "testpassword123",
        }

        response = client.post("/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    def test_register_user_missing_fields(self, client: TestClient):
        """Test registration with missing required fields."""
        user_data = {
            "username": "newuser"
            # Missing email and password
        }

        response = client.post("/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    def test_register_user_empty_fields(self, client: TestClient):
        """Test registration with empty fields."""
        user_data = {"username": "", "email": "", "password": ""}

        response = client.post("/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Test user login endpoint."""

    def test_login_user_success(
        self, client: TestClient, sample_user, sample_user_data
    ):
        """Test successful user login."""
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"],
        }

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Verify token is valid JWT
        token = data["access_token"]
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["sub"] == sample_user_data["username"]

    def test_login_user_wrong_username(
        self, client: TestClient, sample_user, sample_user_data
    ):
        """Test login with incorrect username."""
        login_data = {"username": "wronguser", "password": sample_user_data["password"]}

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_user_wrong_password(
        self, client: TestClient, sample_user, sample_user_data
    ):
        """Test login with incorrect password."""
        login_data = {
            "username": sample_user_data["username"],
            "password": "wrongpassword",
        }

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_user_missing_fields(self, client: TestClient):
        """Test login with missing fields."""
        login_data = {
            "username": "testuser"
            # Missing password
        }

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 422  # Validation error

    def test_login_user_empty_credentials(self, client: TestClient):
        """Test login with empty credentials."""
        login_data = {"username": "", "password": ""}

        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401


class TestGetCurrentUser:
    """Test get current user endpoint."""

    def test_get_current_user_success(
        self, client: TestClient, sample_user, auth_headers
    ):
        """Test successful retrieval of current user."""
        response = client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_user.id
        assert data["username"] == sample_user.username
        assert data["email"] == sample_user.email
        assert "created_at" in data
        assert "hashed_password" not in data

    def test_get_current_user_no_token(self, client: TestClient):
        """Test get current user without authentication token."""
        response = client.get("/auth/me")

        assert response.status_code == 403  # No Authorization header

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test get current user with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 401

    def test_get_current_user_expired_token(self, client: TestClient, sample_user):
        """Test get current user with expired token."""
        # Create expired token
        expired_time = datetime.utcnow() - timedelta(minutes=1)
        expired_token = jwt.encode(
            {"sub": sample_user.username, "exp": expired_time},
            settings.secret_key,
            algorithm=settings.algorithm,
        )

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 401

    def test_get_current_user_nonexistent_user(self, client: TestClient):
        """Test get current user with token for non-existent user."""
        # Create token for non-existent user
        token = jwt.encode(
            {
                "sub": "nonexistentuser",
                "exp": datetime.utcnow() + timedelta(minutes=30),
            },
            settings.secret_key,
            algorithm=settings.algorithm,
        )

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 401

    def test_get_current_user_malformed_auth_header(
        self, client: TestClient, sample_user
    ):
        """Test get current user with malformed authorization header."""
        # Missing 'Bearer' prefix
        token = jwt.encode(
            {
                "sub": sample_user.username,
                "exp": datetime.utcnow() + timedelta(minutes=30),
            },
            settings.secret_key,
            algorithm=settings.algorithm,
        )

        headers = {"Authorization": token}  # Missing "Bearer "
        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 403


class TestAuthenticationFlow:
    """Test complete authentication flow."""

    def test_register_login_and_access_protected_endpoint(self, client: TestClient):
        """Test complete flow: register -> login -> access protected endpoint."""
        # 1. Register user
        user_data = {
            "username": "flowtest",
            "email": "flowtest@example.com",
            "password": "testpassword123",
        }

        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 200

        # 2. Login user
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"],
        }

        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        # 3. Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/auth/me", headers=headers)
        assert me_response.status_code == 200

        user_info = me_response.json()
        assert user_info["username"] == user_data["username"]
        assert user_info["email"] == user_data["email"]

    def test_token_expiration_settings(
        self, client: TestClient, sample_user, sample_user_data
    ):
        """Test that token expiration follows settings."""
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"],
        }

        response = client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]

        # Decode token and check expiration
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        # Token should expire according to settings
        expected_exp = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        actual_exp = datetime.fromtimestamp(payload["exp"])

        # Allow 1 second tolerance
        assert abs((expected_exp - actual_exp).total_seconds()) < 1
