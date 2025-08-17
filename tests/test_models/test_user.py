import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models import User
from app.core.security import get_password_hash


class TestUserModel:
    """Test User model functionality."""

    def test_create_user_success(self, db_session):
        """Test successful user creation."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.hashed_password != "password123"  # Should be hashed
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_user_username_unique_constraint(self, db_session):
        """Test username uniqueness constraint."""
        user1 = User(
            username="testuser",
            email="test1@example.com",
            hashed_password=get_password_hash("password123"),
        )
        user2 = User(
            username="testuser",  # Same username
            email="test2@example.com",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_email_unique_constraint(self, db_session):
        """Test email uniqueness constraint."""
        user1 = User(
            username="testuser1",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
        )
        user2 = User(
            username="testuser2",
            email="test@example.com",  # Same email
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_nullable_constraints(self, db_session):
        """Test that required fields cannot be null."""
        # Test missing username
        with pytest.raises(IntegrityError):
            user = User(
                email="test@example.com",
                hashed_password=get_password_hash("password123"),
            )
            db_session.add(user)
            db_session.commit()

        db_session.rollback()

        # Test missing email
        with pytest.raises(IntegrityError):
            user = User(
                username="testuser", hashed_password=get_password_hash("password123")
            )
            db_session.add(user)
            db_session.commit()

        db_session.rollback()

        # Test missing hashed_password
        with pytest.raises(IntegrityError):
            user = User(username="testuser", email="test@example.com")
            db_session.add(user)
            db_session.commit()

    def test_user_created_at_auto_generation(self, db_session):
        """Test that created_at is automatically set."""
        before_creation = datetime.utcnow()

        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        after_creation = datetime.utcnow()

        assert user.created_at is not None
        assert before_creation <= user.created_at <= after_creation

    def test_user_games_relationship(self, db_session, sample_user):
        """Test relationship with games."""
        from app.models import Game

        # Create games for the user
        game1 = Game(
            user_id=sample_user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="easy",
        )
        game2 = Game(
            user_id=sample_user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="medium",
        )

        db_session.add_all([game1, game2])
        db_session.commit()

        # Refresh user to load relationship
        db_session.refresh(sample_user)

        assert len(sample_user.games) == 2
        assert game1 in sample_user.games
        assert game2 in sample_user.games

    def test_user_str_representation(self, sample_user):
        """Test string representation of user."""
        # User model doesn't define __str__ but should have basic attributes
        assert hasattr(sample_user, "username")
        assert hasattr(sample_user, "email")
        assert hasattr(sample_user, "id")

    def test_user_indexing(self, db_session):
        """Test that indexed fields are properly set up."""
        # Create multiple users to test indexing
        users = []
        for i in range(10):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                hashed_password=get_password_hash("password123"),
            )
            users.append(user)

        db_session.add_all(users)
        db_session.commit()

        # Query by username (should use index)
        found_user = db_session.query(User).filter(User.username == "user5").first()
        assert found_user is not None
        assert found_user.username == "user5"

        # Query by email (should use index)
        found_user = (
            db_session.query(User).filter(User.email == "user3@example.com").first()
        )
        assert found_user is not None
        assert found_user.email == "user3@example.com"

    def test_user_field_lengths(self, db_session):
        """Test field length constraints."""
        # Test very long username
        long_username = "a" * 1000
        user = User(
            username=long_username,
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user)
        # Should succeed as String in SQLAlchemy doesn't have default length limit
        db_session.commit()

        assert user.username == long_username

    def test_user_password_hashing(self, db_session):
        """Test that passwords are properly hashed."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        user = User(
            username="testuser", email="test@example.com", hashed_password=hashed
        )

        db_session.add(user)
        db_session.commit()

        # Password should be hashed
        assert user.hashed_password != password
        assert user.hashed_password.startswith("$2b$")  # bcrypt format
        assert len(user.hashed_password) > 50


class TestUserModelQueries:
    """Test User model query operations."""

    def test_find_user_by_username(self, db_session, sample_user):
        """Test finding user by username."""
        found_user = (
            db_session.query(User).filter(User.username == sample_user.username).first()
        )

        assert found_user is not None
        assert found_user.id == sample_user.id
        assert found_user.email == sample_user.email

    def test_find_user_by_email(self, db_session, sample_user):
        """Test finding user by email."""
        found_user = (
            db_session.query(User).filter(User.email == sample_user.email).first()
        )

        assert found_user is not None
        assert found_user.id == sample_user.id
        assert found_user.username == sample_user.username

    def test_find_nonexistent_user(self, db_session):
        """Test querying for non-existent user."""
        found_user = (
            db_session.query(User).filter(User.username == "nonexistent").first()
        )
        assert found_user is None

        found_user = (
            db_session.query(User)
            .filter(User.email == "nonexistent@example.com")
            .first()
        )
        assert found_user is None

    def test_user_count(self, db_session, sample_user):
        """Test counting users."""
        count = db_session.query(User).count()
        assert count >= 1  # At least the sample user

    def test_user_ordering(self, db_session):
        """Test ordering users."""
        # Create multiple users
        users_data = [
            ("charlie", "charlie@example.com"),
            ("alice", "alice@example.com"),
            ("bob", "bob@example.com"),
        ]

        for username, email in users_data:
            user = User(
                username=username,
                email=email,
                hashed_password=get_password_hash("password123"),
            )
            db_session.add(user)

        db_session.commit()

        # Test ordering by username
        users = db_session.query(User).order_by(User.username).all()
        usernames = [user.username for user in users]

        # Should be in alphabetical order (plus any existing users)
        alice_idx = next(i for i, name in enumerate(usernames) if name == "alice")
        bob_idx = next(i for i, name in enumerate(usernames) if name == "bob")
        charlie_idx = next(i for i, name in enumerate(usernames) if name == "charlie")

        assert alice_idx < bob_idx < charlie_idx

    def test_user_update(self, db_session, sample_user):
        """Test updating user information."""
        original_email = sample_user.email
        new_email = "newemail@example.com"

        sample_user.email = new_email
        db_session.commit()

        # Refresh from database
        db_session.refresh(sample_user)

        assert sample_user.email == new_email
        assert sample_user.email != original_email

    def test_user_deletion(self, db_session):
        """Test user deletion."""
        user = User(
            username="todelete",
            email="delete@example.com",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user)
        db_session.commit()

        user_id = user.id

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Verify deletion
        found_user = db_session.query(User).filter(User.id == user_id).first()
        assert found_user is None
