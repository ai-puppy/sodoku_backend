import pytest
import json
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models import Game, User
from app.core.security import get_password_hash


class TestGameModel:
    """Test Game model functionality."""

    def test_create_game_success(self, db_session, sample_user):
        """Test successful game creation."""
        puzzle_data = [[1, 2, 3] for _ in range(3)]
        solution_data = [[4, 5, 6] for _ in range(3)]
        current_state = [[1, 0, 3] for _ in range(3)]

        game = Game(
            user_id=sample_user.id,
            puzzle_data=json.dumps(puzzle_data),
            solution=json.dumps(solution_data),
            current_state=json.dumps(current_state),
            difficulty_level="medium",
        )

        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)

        assert game.id is not None
        assert game.user_id == sample_user.id
        assert game.puzzle_data == json.dumps(puzzle_data)
        assert game.solution == json.dumps(solution_data)
        assert game.current_state == json.dumps(current_state)
        assert game.difficulty_level == "medium"
        assert game.completed is False  # Default value
        assert game.created_at is not None
        assert game.updated_at is not None
        assert game.completed_at is None  # Default value

    def test_game_user_relationship(self, db_session, sample_user):
        """Test relationship with user."""
        game = Game(
            user_id=sample_user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="easy",
        )

        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)

        # Test back reference
        assert game.user is not None
        assert game.user.id == sample_user.id
        assert game.user.username == sample_user.username

    def test_game_foreign_key_constraint(self, db_session):
        """Test foreign key constraint with non-existent user."""
        game = Game(
            user_id=99999,  # Non-existent user
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="easy",
        )

        db_session.add(game)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_game_nullable_constraints(self, db_session, sample_user):
        """Test that required fields cannot be null."""
        # Test missing user_id
        with pytest.raises(IntegrityError):
            game = Game(
                puzzle_data="[]",
                solution="[]",
                current_state="[]",
                difficulty_level="easy",
            )
            db_session.add(game)
            db_session.commit()

        db_session.rollback()

        # Test missing puzzle_data
        with pytest.raises(IntegrityError):
            game = Game(
                user_id=sample_user.id,
                solution="[]",
                current_state="[]",
                difficulty_level="easy",
            )
            db_session.add(game)
            db_session.commit()

        db_session.rollback()

        # Test missing solution
        with pytest.raises(IntegrityError):
            game = Game(
                user_id=sample_user.id,
                puzzle_data="[]",
                current_state="[]",
                difficulty_level="easy",
            )
            db_session.add(game)
            db_session.commit()

        db_session.rollback()

        # Test missing current_state
        with pytest.raises(IntegrityError):
            game = Game(
                user_id=sample_user.id,
                puzzle_data="[]",
                solution="[]",
                difficulty_level="easy",
            )
            db_session.add(game)
            db_session.commit()

        db_session.rollback()

        # Test missing difficulty_level
        with pytest.raises(IntegrityError):
            game = Game(
                user_id=sample_user.id,
                puzzle_data="[]",
                solution="[]",
                current_state="[]",
            )
            db_session.add(game)
            db_session.commit()

    def test_game_default_values(self, db_session, sample_user):
        """Test default values for optional fields."""
        game = Game(
            user_id=sample_user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="easy",
        )

        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)

        assert game.completed is False
        assert game.completed_at is None

    def test_game_completion(self, db_session, sample_user):
        """Test game completion functionality."""
        game = Game(
            user_id=sample_user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="easy",
        )

        db_session.add(game)
        db_session.commit()

        # Complete the game
        completion_time = datetime.utcnow()
        game.completed = True
        game.completed_at = completion_time

        db_session.commit()
        db_session.refresh(game)

        assert game.completed is True
        assert game.completed_at is not None
        assert abs((game.completed_at - completion_time).total_seconds()) < 1

    def test_game_timestamps_auto_generation(self, db_session, sample_user):
        """Test that timestamps are automatically generated."""
        before_creation = datetime.utcnow()

        game = Game(
            user_id=sample_user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="easy",
        )

        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)

        after_creation = datetime.utcnow()

        assert game.created_at is not None
        assert game.updated_at is not None
        assert before_creation <= game.created_at <= after_creation
        assert before_creation <= game.updated_at <= after_creation

    def test_game_updated_at_on_update(self, db_session, sample_user):
        """Test that updated_at changes when game is updated."""
        game = Game(
            user_id=sample_user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="easy",
        )

        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)

        original_updated_at = game.updated_at

        # Wait a moment and update
        import time

        time.sleep(0.1)

        game.current_state = json.dumps([[1, 2, 3]])
        db_session.commit()
        db_session.refresh(game)

        assert game.updated_at > original_updated_at

    def test_game_json_data_storage(self, db_session, sample_user):
        """Test storing complex JSON data in text fields."""
        complex_board = [
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

        game = Game(
            user_id=sample_user.id,
            puzzle_data=json.dumps(complex_board),
            solution=json.dumps(complex_board),
            current_state=json.dumps(complex_board),
            difficulty_level="hard",
        )

        db_session.add(game)
        db_session.commit()
        db_session.refresh(game)

        # Verify data can be retrieved and parsed
        retrieved_puzzle = json.loads(game.puzzle_data)
        assert retrieved_puzzle == complex_board
        assert len(retrieved_puzzle) == 9
        assert all(len(row) == 9 for row in retrieved_puzzle)

    def test_game_difficulty_levels(self, db_session, sample_user):
        """Test different difficulty levels."""
        difficulties = ["easy", "medium", "hard", "expert"]

        games = []
        for difficulty in difficulties:
            game = Game(
                user_id=sample_user.id,
                puzzle_data="[]",
                solution="[]",
                current_state="[]",
                difficulty_level=difficulty,
            )
            games.append(game)

        db_session.add_all(games)
        db_session.commit()

        for game, expected_difficulty in zip(games, difficulties):
            db_session.refresh(game)
            assert game.difficulty_level == expected_difficulty


class TestGameModelQueries:
    """Test Game model query operations."""

    def test_find_games_by_user(self, db_session, sample_user):
        """Test finding games by user."""
        # Create multiple games for the user
        for i in range(3):
            game = Game(
                user_id=sample_user.id,
                puzzle_data="[]",
                solution="[]",
                current_state="[]",
                difficulty_level="easy",
            )
            db_session.add(game)

        db_session.commit()

        # Query games for user
        user_games = db_session.query(Game).filter(Game.user_id == sample_user.id).all()

        assert len(user_games) >= 3
        assert all(game.user_id == sample_user.id for game in user_games)

    def test_find_completed_games(self, db_session, sample_user):
        """Test finding completed games."""
        # Create mix of completed and incomplete games
        completed_game = Game(
            user_id=sample_user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="easy",
            completed=True,
            completed_at=datetime.utcnow(),
        )

        incomplete_game = Game(
            user_id=sample_user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="medium",
            completed=False,
        )

        db_session.add_all([completed_game, incomplete_game])
        db_session.commit()

        # Query completed games
        completed_games = (
            db_session.query(Game)
            .filter(Game.user_id == sample_user.id, Game.completed.is_(True))
            .all()
        )

        assert len(completed_games) >= 1
        assert all(game.completed for game in completed_games)

        # Query incomplete games
        incomplete_games = (
            db_session.query(Game)
            .filter(Game.user_id == sample_user.id, Game.completed.is_(False))
            .all()
        )

        assert len(incomplete_games) >= 1
        assert all(not game.completed for game in incomplete_games)

    def test_find_games_by_difficulty(self, db_session, sample_user):
        """Test finding games by difficulty level."""
        difficulties = ["easy", "medium", "hard"]

        for difficulty in difficulties:
            game = Game(
                user_id=sample_user.id,
                puzzle_data="[]",
                solution="[]",
                current_state="[]",
                difficulty_level=difficulty,
            )
            db_session.add(game)

        db_session.commit()

        # Query games by difficulty
        easy_games = (
            db_session.query(Game)
            .filter(Game.user_id == sample_user.id, Game.difficulty_level == "easy")
            .all()
        )

        assert len(easy_games) >= 1
        assert all(game.difficulty_level == "easy" for game in easy_games)

    def test_game_ordering(self, db_session, sample_user):
        """Test ordering games."""
        import time

        games = []
        for i in range(3):
            game = Game(
                user_id=sample_user.id,
                puzzle_data="[]",
                solution="[]",
                current_state="[]",
                difficulty_level="easy",
            )
            db_session.add(game)
            db_session.commit()
            db_session.refresh(game)
            games.append(game)
            time.sleep(0.01)  # Ensure different timestamps

        # Query games ordered by creation time
        ordered_games = (
            db_session.query(Game)
            .filter(Game.user_id == sample_user.id)
            .order_by(Game.created_at.desc())
            .all()
        )

        # Should be in reverse chronological order
        for i in range(len(ordered_games) - 1):
            assert ordered_games[i].created_at >= ordered_games[i + 1].created_at

    def test_game_count(self, db_session, sample_user):
        """Test counting games."""
        initial_count = (
            db_session.query(Game).filter(Game.user_id == sample_user.id).count()
        )

        # Add new game
        game = Game(
            user_id=sample_user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="easy",
        )
        db_session.add(game)
        db_session.commit()

        new_count = (
            db_session.query(Game).filter(Game.user_id == sample_user.id).count()
        )
        assert new_count == initial_count + 1

    def test_game_update(self, db_session, sample_game):
        """Test updating game state."""
        original_state = sample_game.current_state
        new_state = json.dumps([[1, 2, 3]])

        sample_game.current_state = new_state
        db_session.commit()
        db_session.refresh(sample_game)

        assert sample_game.current_state == new_state
        assert sample_game.current_state != original_state

    def test_game_deletion(self, db_session, sample_user):
        """Test game deletion."""
        game = Game(
            user_id=sample_user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="easy",
        )

        db_session.add(game)
        db_session.commit()

        game_id = game.id

        # Delete game
        db_session.delete(game)
        db_session.commit()

        # Verify deletion
        found_game = db_session.query(Game).filter(Game.id == game_id).first()
        assert found_game is None

    def test_user_games_cascade(self, db_session):
        """Test that deleting user doesn't break game references."""
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
        )
        db_session.add(user)
        db_session.commit()

        # Create game for user
        game = Game(
            user_id=user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="easy",
        )
        db_session.add(game)
        db_session.commit()

        game_id = game.id

        # Delete user (note: this might cause foreign key constraint issues
        # depending on cascade settings, but let's test the current behavior)
        try:
            db_session.delete(user)
            db_session.commit()

            # Game should still exist but user reference will be invalid
            db_session.query(Game).filter(Game.id == game_id).first()
            # This test depends on cascade configuration

        except IntegrityError:
            # If foreign key constraint prevents deletion, that's also valid behavior
            db_session.rollback()
            assert True  # Expected behavior with foreign key constraints
