import pytest
import tempfile
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker

from app.main import app
from app.database import Base, get_db
from app.models import User, Game
from app.core.security import get_password_hash, create_access_token
from app.config import Settings


fake = Faker()


@pytest.fixture(scope="session")
def test_db():
    """Create a temporary SQLite database for testing."""
    db_fd, db_path = tempfile.mkstemp()
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    try:
        yield TestingSessionLocal
    finally:
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Create a fresh database session for each test."""
    session = test_db()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with test database."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_settings():
    """Test settings with overrides."""
    return Settings(
        database_url="sqlite:///test.db",
        secret_key="test-secret-key",
        algorithm="HS256",
        access_token_expire_minutes=30,
    )


@pytest.fixture
def sample_user_data():
    """Generate sample user registration data."""
    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": "testpassword123",
    }


@pytest.fixture
def sample_user(db_session, sample_user_data):
    """Create a sample user in the database."""
    hashed_password = get_password_hash(sample_user_data["password"])
    user = User(
        username=sample_user_data["username"],
        email=sample_user_data["email"],
        hashed_password=hashed_password,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(sample_user):
    """Create authentication headers for a test user."""
    token = create_access_token(data={"sub": sample_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_game_data():
    """Generate sample game creation data."""
    return {"difficulty_level": "medium"}


@pytest.fixture
def sample_sudoku_board():
    """Provide a sample valid Sudoku board."""
    return [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]


@pytest.fixture
def sample_sudoku_solution():
    """Provide the solution for the sample Sudoku board."""
    return [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]


@pytest.fixture
def invalid_sudoku_board():
    """Provide an invalid Sudoku board for testing validation."""
    return [
        [5, 5, 0, 0, 7, 0, 0, 0, 0],  # Duplicate 5 in first row
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]


@pytest.fixture
def sample_game(db_session, sample_user, sample_sudoku_board, sample_sudoku_solution):
    """Create a sample game in the database."""
    import json

    game = Game(
        user_id=sample_user.id,
        puzzle_data=json.dumps(sample_sudoku_board),
        solution=json.dumps(sample_sudoku_solution),
        current_state=json.dumps(sample_sudoku_board),
        difficulty_level="medium",
    )
    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)
    return game


@pytest.fixture(autouse=True)
def mock_settings(test_settings):
    """Mock the settings for all tests."""
    with patch("app.config.settings", test_settings):
        yield test_settings
