import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas import (
    GameBase,
    GameCreate,
    GameUpdate,
    Game,
    GameResponse,
    NextGameResponse,
)


class TestGameBase:
    """Test GameBase schema."""

    def test_game_base_valid(self):
        """Test valid GameBase creation."""
        game_data = {"difficulty_level": "medium"}

        game_base = GameBase(**game_data)

        assert game_base.difficulty_level == "medium"

    def test_game_base_all_difficulties(self):
        """Test GameBase with all valid difficulty levels."""
        valid_difficulties = ["easy", "medium", "hard", "expert"]

        for difficulty in valid_difficulties:
            game_base = GameBase(difficulty_level=difficulty)
            assert game_base.difficulty_level == difficulty

    def test_game_base_custom_difficulty(self):
        """Test GameBase with custom difficulty level."""
        # Schema doesn't restrict difficulty values, so custom values should work
        game_base = GameBase(difficulty_level="impossible")
        assert game_base.difficulty_level == "impossible"

    def test_game_base_missing_difficulty(self):
        """Test GameBase with missing difficulty level."""
        with pytest.raises(ValidationError):
            GameBase()

    def test_game_base_empty_difficulty(self):
        """Test GameBase with empty difficulty level."""
        # Pydantic allows empty strings by default
        game_base = GameBase(difficulty_level="")
        assert game_base.difficulty_level == ""

    def test_game_base_difficulty_types(self):
        """Test GameBase with different difficulty types."""
        # String should work
        game_base = GameBase(difficulty_level="easy")
        assert isinstance(game_base.difficulty_level, str)

        # Non-string should fail validation in Pydantic v2
        with pytest.raises(ValidationError):
            GameBase(difficulty_level=123)


class TestGameCreate:
    """Test GameCreate schema."""

    def test_game_create_valid(self):
        """Test valid GameCreate creation."""
        game_data = {"difficulty_level": "hard"}

        game_create = GameCreate(**game_data)

        assert game_create.difficulty_level == "hard"

    def test_game_create_inherits_from_game_base(self):
        """Test that GameCreate inherits GameBase validation."""
        # Should fail with missing difficulty
        with pytest.raises(ValidationError):
            GameCreate()

    def test_game_create_all_difficulties(self):
        """Test GameCreate with all difficulty levels."""
        difficulties = ["easy", "medium", "hard", "expert"]

        for difficulty in difficulties:
            game_create = GameCreate(difficulty_level=difficulty)
            assert game_create.difficulty_level == difficulty


class TestGameUpdate:
    """Test GameUpdate schema."""

    def test_game_update_valid(self):
        """Test valid GameUpdate creation."""
        board = [
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

        game_update = GameUpdate(current_state=board)

        assert game_update.current_state == board
        assert len(game_update.current_state) == 9
        assert all(len(row) == 9 for row in game_update.current_state)

    def test_game_update_partial_board(self):
        """Test GameUpdate with partial Sudoku board."""
        partial_board = [
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

        game_update = GameUpdate(current_state=partial_board)

        assert game_update.current_state == partial_board
        # Check that zeros (empty cells) are preserved
        assert any(0 in row for row in game_update.current_state)

    def test_game_update_missing_current_state(self):
        """Test GameUpdate with missing current_state."""
        with pytest.raises(ValidationError):
            GameUpdate()

    def test_game_update_invalid_board_dimensions(self):
        """Test GameUpdate with invalid board dimensions."""
        # Wrong number of rows
        invalid_board = [[1, 2, 3, 4, 5, 6, 7, 8, 9] for _ in range(8)]  # Only 8 rows

        # Pydantic doesn't validate nested list dimensions by default
        # This might pass schema validation but fail business logic
        game_update = GameUpdate(current_state=invalid_board)
        assert len(game_update.current_state) == 8

        # Wrong number of columns
        invalid_board = [
            [1, 2, 3, 4, 5, 6, 7, 8] for _ in range(9)
        ]  # Only 8 columns per row

        game_update = GameUpdate(current_state=invalid_board)
        assert all(len(row) == 8 for row in game_update.current_state)

    def test_game_update_invalid_cell_values(self):
        """Test GameUpdate with invalid cell values."""
        # Values outside 0-9 range
        invalid_board = [
            [10, 3, 4, 6, 7, 8, 9, 1, 2],  # 10 is invalid
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, -1],  # -1 is invalid
        ]

        # Schema validation might not catch this
        game_update = GameUpdate(current_state=invalid_board)
        assert game_update.current_state[0][0] == 10
        assert game_update.current_state[8][8] == -1

    def test_game_update_non_integer_values(self):
        """Test GameUpdate with non-integer cell values."""
        # String values
        board_with_strings = [
            ["5", "3", "4", "6", "7", "8", "9", "1", "2"],
            ["6", "7", "2", "1", "9", "5", "3", "4", "8"],
            ["1", "9", "8", "3", "4", "2", "5", "6", "7"],
            ["8", "5", "9", "7", "6", "1", "4", "2", "3"],
            ["4", "2", "6", "8", "5", "3", "7", "9", "1"],
            ["7", "1", "3", "9", "2", "4", "8", "5", "6"],
            ["9", "6", "1", "5", "3", "7", "2", "8", "4"],
            ["2", "8", "7", "4", "1", "9", "6", "3", "5"],
            ["3", "4", "5", "2", "8", "6", "1", "7", "9"],
        ]

        # Pydantic should convert strings to integers
        game_update = GameUpdate(current_state=board_with_strings)
        assert all(
            isinstance(cell, int) for row in game_update.current_state for cell in row
        )


class TestGame:
    """Test Game schema."""

    def test_game_valid(self):
        """Test valid Game creation."""
        board = [[1, 2, 3] for _ in range(3)]

        game_data = {
            "id": 1,
            "user_id": 1,
            "puzzle_data": board,
            "solution": board,
            "current_state": board,
            "difficulty_level": "easy",
            "completed": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        game = Game(**game_data)

        assert game.id == 1
        assert game.user_id == 1
        assert game.puzzle_data == board
        assert game.solution == board
        assert game.current_state == board
        assert game.difficulty_level == "easy"
        assert game.completed is False
        assert isinstance(game.created_at, datetime)
        assert isinstance(game.updated_at, datetime)
        assert game.completed_at is None

    def test_game_with_completed_at(self):
        """Test Game with completed_at timestamp."""
        board = [[1, 2, 3] for _ in range(3)]
        completion_time = datetime.utcnow()

        game_data = {
            "id": 1,
            "user_id": 1,
            "puzzle_data": board,
            "solution": board,
            "current_state": board,
            "difficulty_level": "hard",
            "completed": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_at": completion_time,
        }

        game = Game(**game_data)

        assert game.completed is True
        assert game.completed_at == completion_time

    def test_game_inherits_from_game_base(self):
        """Test that Game inherits GameBase validation."""
        board = [[1, 2, 3] for _ in range(3)]

        # Should fail with missing difficulty_level
        with pytest.raises(ValidationError):
            Game(
                id=1,
                user_id=1,
                puzzle_data=board,
                solution=board,
                current_state=board,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

    def test_game_missing_required_fields(self):
        """Test Game with missing required fields."""
        board = [[1, 2, 3] for _ in range(3)]
        base_data = {
            "user_id": 1,
            "puzzle_data": board,
            "solution": board,
            "current_state": board,
            "difficulty_level": "easy",
            "completed": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        # Test missing each required field
        required_fields = ["id", "user_id", "puzzle_data", "solution", "current_state"]

        for field in required_fields:
            with pytest.raises(ValidationError):
                Game(**{k: v for k, v in base_data.items() if k != field})

    def test_game_config(self):
        """Test Game model config."""
        board = [[1, 2, 3] for _ in range(3)]

        game_data = {
            "id": 1,
            "user_id": 1,
            "puzzle_data": board,
            "solution": board,
            "current_state": board,
            "difficulty_level": "easy",
            "completed": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        # Test from_attributes config
        class MockORM:
            def __init__(self):
                for key, value in game_data.items():
                    setattr(self, key, value)

        mock_orm = MockORM()
        game_from_orm = Game.model_validate(mock_orm)

        assert game_from_orm.id == game_data["id"]
        assert game_from_orm.difficulty_level == game_data["difficulty_level"]


class TestGameResponse:
    """Test GameResponse schema."""

    def test_game_response_valid(self):
        """Test valid GameResponse creation."""
        board = [[1, 2, 3] for _ in range(3)]

        response_data = {
            "id": 1,
            "puzzle_data": board,
            "current_state": board,
            "difficulty_level": "medium",
            "completed": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
        }

        game_response = GameResponse(**response_data)

        assert game_response.id == 1
        assert game_response.puzzle_data == board
        assert game_response.current_state == board
        assert game_response.difficulty_level == "medium"
        assert game_response.completed is True
        assert isinstance(game_response.created_at, datetime)
        assert isinstance(game_response.updated_at, datetime)
        assert isinstance(game_response.completed_at, datetime)

    def test_game_response_no_completion(self):
        """Test GameResponse for incomplete game."""
        board = [[1, 2, 3] for _ in range(3)]

        response_data = {
            "id": 1,
            "puzzle_data": board,
            "current_state": board,
            "difficulty_level": "expert",
            "completed": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        game_response = GameResponse(**response_data)

        assert game_response.completed is False
        assert game_response.completed_at is None

    def test_game_response_missing_fields(self):
        """Test GameResponse with missing required fields."""
        board = [[1, 2, 3] for _ in range(3)]
        base_data = {
            "puzzle_data": board,
            "current_state": board,
            "difficulty_level": "easy",
            "completed": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        # Missing id should fail
        with pytest.raises(ValidationError):
            GameResponse(**base_data)

    def test_game_response_config(self):
        """Test GameResponse model config."""
        board = [[1, 2, 3] for _ in range(3)]

        response_data = {
            "id": 1,
            "puzzle_data": board,
            "current_state": board,
            "difficulty_level": "easy",
            "completed": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        # Test from_attributes config
        class MockORM:
            def __init__(self):
                for key, value in response_data.items():
                    setattr(self, key, value)

        mock_orm = MockORM()
        response_from_orm = GameResponse.model_validate(mock_orm)

        assert response_from_orm.id == response_data["id"]
        assert response_from_orm.completed == response_data["completed"]


class TestNextGameResponse:
    """Test NextGameResponse schema."""

    def test_next_game_response_with_next_game(self):
        """Test NextGameResponse when there is a next game."""
        response_data = {
            "has_next": True,
            "next_game_id": 123,
            "suggested_difficulty": "medium",
        }

        next_game_response = NextGameResponse(**response_data)

        assert next_game_response.has_next is True
        assert next_game_response.next_game_id == 123
        assert next_game_response.suggested_difficulty == "medium"

    def test_next_game_response_no_next_game(self):
        """Test NextGameResponse when there is no next game."""
        response_data = {"has_next": False, "suggested_difficulty": "easy"}

        next_game_response = NextGameResponse(**response_data)

        assert next_game_response.has_next is False
        assert next_game_response.next_game_id is None  # Default value
        assert next_game_response.suggested_difficulty == "easy"

    def test_next_game_response_explicit_none(self):
        """Test NextGameResponse with explicit None for next_game_id."""
        response_data = {
            "has_next": False,
            "next_game_id": None,
            "suggested_difficulty": "hard",
        }

        next_game_response = NextGameResponse(**response_data)

        assert next_game_response.has_next is False
        assert next_game_response.next_game_id is None
        assert next_game_response.suggested_difficulty == "hard"

    def test_next_game_response_missing_required_fields(self):
        """Test NextGameResponse with missing required fields."""
        # Missing has_next
        with pytest.raises(ValidationError):
            NextGameResponse(suggested_difficulty="easy")

        # Missing suggested_difficulty
        with pytest.raises(ValidationError):
            NextGameResponse(has_next=True)

    def test_next_game_response_invalid_types(self):
        """Test NextGameResponse with invalid field types."""
        # Invalid has_next type
        response_data = {
            "has_next": "true",  # String instead of bool
            "suggested_difficulty": "easy",
        }

        # Pydantic should convert string to bool
        next_game_response = NextGameResponse(**response_data)
        assert next_game_response.has_next is True
        assert isinstance(next_game_response.has_next, bool)

        # Invalid next_game_id type
        response_data = {
            "has_next": True,
            "next_game_id": "123",  # String instead of int
            "suggested_difficulty": "easy",
        }

        # Pydantic should convert string to int
        next_game_response = NextGameResponse(**response_data)
        assert next_game_response.next_game_id == 123
        assert isinstance(next_game_response.next_game_id, int)


class TestSchemaIntegration:
    """Test schema integration and real-world scenarios."""

    def test_game_creation_flow(self):
        """Test complete game creation flow with schemas."""
        # Start with GameCreate
        game_create = GameCreate(difficulty_level="medium")

        # Simulate game creation response
        board = [[0 for _ in range(9)] for _ in range(9)]

        game_response = GameResponse(
            id=1,
            puzzle_data=board,
            current_state=board,
            difficulty_level=game_create.difficulty_level,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert game_response.difficulty_level == "medium"
        assert game_response.completed is False

    def test_game_update_flow(self):
        """Test game update flow with schemas."""
        # Initial board state
        initial_board = [[0 for _ in range(9)] for _ in range(9)]

        # Updated board state
        updated_board = [row[:] for row in initial_board]  # Deep copy
        updated_board[0][0] = 5

        game_update = GameUpdate(current_state=updated_board)

        assert game_update.current_state[0][0] == 5
        assert game_update.current_state != initial_board

    def test_serialization_compatibility(self):
        """Test that schemas are compatible with JSON serialization."""
        board = [[1, 2, 3] for _ in range(3)]

        game_response = GameResponse(
            id=1,
            puzzle_data=board,
            current_state=board,
            difficulty_level="easy",
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Should be able to convert to dict for JSON serialization
        response_dict = game_response.model_dump()

        assert isinstance(response_dict, dict)
        assert response_dict["id"] == 1
        assert response_dict["puzzle_data"] == board
        assert isinstance(response_dict["created_at"], datetime)
