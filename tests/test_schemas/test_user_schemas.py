import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas import UserBase, UserCreate, UserLogin, User, Token, TokenData


class TestUserBase:
    """Test UserBase schema."""

    def test_user_base_valid(self):
        """Test valid UserBase creation."""
        user_data = {"username": "testuser", "email": "test@example.com"}

        user_base = UserBase(**user_data)

        assert user_base.username == "testuser"
        assert user_base.email == "test@example.com"

    def test_user_base_invalid_email(self):
        """Test UserBase with invalid email format."""
        user_data = {"username": "testuser", "email": "invalid-email"}

        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)

        assert "email" in str(exc_info.value)

    def test_user_base_missing_fields(self):
        """Test UserBase with missing required fields."""
        # Missing username
        with pytest.raises(ValidationError):
            UserBase(email="test@example.com")

        # Missing email
        with pytest.raises(ValidationError):
            UserBase(username="testuser")

        # Missing both
        with pytest.raises(ValidationError):
            UserBase()

    def test_user_base_empty_strings(self):
        """Test UserBase with empty string values."""
        # Pydantic allows empty strings by default
        user_base = UserBase(username="", email="test@example.com")
        assert user_base.username == ""

        # Empty email should fail validation
        with pytest.raises(ValidationError):
            UserBase(username="testuser", email="")

    def test_user_base_whitespace_handling(self):
        """Test UserBase with whitespace in fields."""
        user_data = {"username": "  testuser  ", "email": "  test@example.com  "}

        user_base = UserBase(**user_data)

        # Username should preserve whitespace
        assert user_base.username == "  testuser  "
        # EmailStr automatically strips whitespace and normalizes
        assert user_base.email == "test@example.com"


class TestUserCreate:
    """Test UserCreate schema."""

    def test_user_create_valid(self):
        """Test valid UserCreate creation."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
        }

        user_create = UserCreate(**user_data)

        assert user_create.username == "testuser"
        assert user_create.email == "test@example.com"
        assert user_create.password == "securepassword123"

    def test_user_create_inherits_from_user_base(self):
        """Test that UserCreate inherits UserBase validation."""
        # Should fail with invalid email
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser", email="invalid-email", password="password123"
            )

    def test_user_create_missing_password(self):
        """Test UserCreate with missing password."""
        with pytest.raises(ValidationError):
            UserCreate(username="testuser", email="test@example.com")

    def test_user_create_empty_password(self):
        """Test UserCreate with empty password."""
        # Pydantic allows empty strings by default
        user_create = UserCreate(
            username="testuser", email="test@example.com", password=""
        )
        assert user_create.password == ""

    def test_user_create_password_types(self):
        """Test UserCreate with different password types."""
        # String password should work
        user_create = UserCreate(
            username="testuser", email="test@example.com", password="password123"
        )
        assert isinstance(user_create.password, str)

        # Non-string password should be converted or fail
        with pytest.raises(ValidationError):
            UserCreate(username="testuser", email="test@example.com", password=123456)


class TestUserLogin:
    """Test UserLogin schema."""

    def test_user_login_valid(self):
        """Test valid UserLogin creation."""
        login_data = {"username": "testuser", "password": "password123"}

        user_login = UserLogin(**login_data)

        assert user_login.username == "testuser"
        assert user_login.password == "password123"

    def test_user_login_missing_fields(self):
        """Test UserLogin with missing fields."""
        # Missing username
        with pytest.raises(ValidationError):
            UserLogin(password="password123")

        # Missing password
        with pytest.raises(ValidationError):
            UserLogin(username="testuser")

        # Missing both
        with pytest.raises(ValidationError):
            UserLogin()

    def test_user_login_empty_fields(self):
        """Test UserLogin with empty fields."""
        # Pydantic allows empty strings by default
        user_login = UserLogin(username="", password="password123")
        assert user_login.username == ""

        user_login = UserLogin(username="testuser", password="")
        assert user_login.password == ""

    def test_user_login_no_email_validation(self):
        """Test that UserLogin doesn't validate email format for username."""
        # Username can be anything, not necessarily email format
        login_data = {"username": "not-an-email", "password": "password123"}

        user_login = UserLogin(**login_data)
        assert user_login.username == "not-an-email"


class TestUser:
    """Test User schema (for responses)."""

    def test_user_valid(self):
        """Test valid User creation."""
        user_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "created_at": datetime.utcnow(),
        }

        user = User(**user_data)

        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert isinstance(user.created_at, datetime)

    def test_user_inherits_from_user_base(self):
        """Test that User inherits UserBase validation."""
        # Should fail with invalid email
        with pytest.raises(ValidationError):
            User(
                id=1,
                username="testuser",
                email="invalid-email",
                created_at=datetime.utcnow(),
            )

    def test_user_missing_required_fields(self):
        """Test User with missing required fields."""
        base_data = {
            "username": "testuser",
            "email": "test@example.com",
            "created_at": datetime.utcnow(),
        }

        # Missing id
        with pytest.raises(ValidationError):
            User(**{k: v for k, v in base_data.items() if k != "id"})

        # Missing created_at
        with pytest.raises(ValidationError):
            User(id=1, **{k: v for k, v in base_data.items() if k != "created_at"})

    def test_user_id_validation(self):
        """Test User ID validation."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "created_at": datetime.utcnow(),
        }

        # Valid positive integer ID
        user = User(id=1, **user_data)
        assert user.id == 1

        # String ID that can be converted to int
        user = User(id="123", **user_data)
        assert user.id == 123
        assert isinstance(user.id, int)

        # Invalid ID types
        with pytest.raises(ValidationError):
            User(id="not-a-number", **user_data)

        with pytest.raises(ValidationError):
            User(id=1.5, **user_data)

    def test_user_datetime_validation(self):
        """Test User datetime validation."""
        user_data = {"id": 1, "username": "testuser", "email": "test@example.com"}

        # Valid datetime
        now = datetime.utcnow()
        user = User(created_at=now, **user_data)
        assert user.created_at == now

        # String datetime that can be parsed
        user = User(created_at="2023-01-01T12:00:00", **user_data)
        assert isinstance(user.created_at, datetime)

        # Invalid datetime
        with pytest.raises(ValidationError):
            User(created_at="not-a-datetime", **user_data)

    def test_user_config(self):
        """Test User model config."""
        # Test that from_attributes is properly set
        user_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "created_at": datetime.utcnow(),
        }

        User(**user_data)

        # Should be able to create from dict (simulating ORM object)
        class MockORM:
            def __init__(self):
                for key, value in user_data.items():
                    setattr(self, key, value)

        mock_orm = MockORM()
        user_from_orm = User.model_validate(mock_orm)

        assert user_from_orm.id == user_data["id"]
        assert user_from_orm.username == user_data["username"]


class TestToken:
    """Test Token schema."""

    def test_token_valid(self):
        """Test valid Token creation."""
        token_data = {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.example",
            "token_type": "bearer",
        }

        token = Token(**token_data)

        assert token.access_token == token_data["access_token"]
        assert token.token_type == "bearer"

    def test_token_missing_fields(self):
        """Test Token with missing fields."""
        # Missing access_token
        with pytest.raises(ValidationError):
            Token(token_type="bearer")

        # Missing token_type
        with pytest.raises(ValidationError):
            Token(access_token="some.token.here")

    def test_token_empty_fields(self):
        """Test Token with empty fields."""
        # Pydantic allows empty strings by default
        token = Token(access_token="", token_type="bearer")
        assert token.access_token == ""

        token = Token(access_token="some.token.here", token_type="")
        assert token.token_type == ""

    def test_token_type_validation(self):
        """Test token_type validation."""
        # Common token types should work
        valid_types = ["bearer", "Bearer", "BEARER", "Basic"]

        for token_type in valid_types:
            token = Token(access_token="some.token.here", token_type=token_type)
            assert token.token_type == token_type


class TestTokenData:
    """Test TokenData schema."""

    def test_token_data_valid(self):
        """Test valid TokenData creation."""
        token_data = TokenData(username="testuser")

        assert token_data.username == "testuser"

    def test_token_data_optional_username(self):
        """Test TokenData with optional username."""
        # Username is optional (can be None)
        token_data = TokenData()
        assert token_data.username is None

        token_data = TokenData(username=None)
        assert token_data.username is None

    def test_token_data_empty_username(self):
        """Test TokenData with empty username."""
        # Empty string should be allowed
        token_data = TokenData(username="")
        assert token_data.username == ""

    def test_token_data_username_types(self):
        """Test TokenData with different username types."""
        # String username
        token_data = TokenData(username="testuser")
        assert token_data.username == "testuser"

        # None username
        token_data = TokenData(username=None)
        assert token_data.username is None


class TestSchemaValidationEdgeCases:
    """Test edge cases and special scenarios."""

    def test_unicode_usernames(self):
        """Test schemas with unicode characters."""
        user_data = {
            "username": "用户名",
            "email": "test@example.com",
            "password": "password123",
        }

        user_create = UserCreate(**user_data)
        assert user_create.username == "用户名"

    def test_long_field_values(self):
        """Test schemas with very long field values."""
        long_username = "a" * 1000
        long_password = "p" * 1000

        user_create = UserCreate(
            username=long_username, email="test@example.com", password=long_password
        )

        assert len(user_create.username) == 1000
        assert len(user_create.password) == 1000

    def test_special_characters_in_fields(self):
        """Test schemas with special characters."""
        user_data = {
            "username": "user!@#$%^&*()",
            "email": "test+tag@example-domain.com",
            "password": "pass!@#$%^&*()",
        }

        user_create = UserCreate(**user_data)
        assert user_create.username == "user!@#$%^&*()"
        assert user_create.email == "test+tag@example-domain.com"

    def test_case_sensitivity(self):
        """Test case sensitivity in schemas."""
        user_data = {
            "username": "TestUser",
            "email": "Test@Example.COM",
            "password": "Password123",
        }

        user_create = UserCreate(**user_data)
        assert user_create.username == "TestUser"
        # EmailStr normalizes email to lowercase
        assert user_create.email == "Test@example.com"

    def test_serialization_roundtrip(self):
        """Test schema serialization and deserialization."""
        user_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "created_at": datetime.utcnow(),
        }

        user = User(**user_data)

        # Serialize to dict
        user_dict = user.model_dump()

        # Deserialize back
        user_restored = User(**user_dict)

        assert user_restored.id == user.id
        assert user_restored.username == user.username
        assert user_restored.email == user.email
        assert user_restored.created_at == user.created_at
