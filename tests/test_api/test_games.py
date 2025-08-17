from fastapi.testclient import TestClient
from datetime import datetime

from app.models import Game


class TestCreateNewGame:
    """Test creating new games."""

    def test_create_new_game_success(
        self, client: TestClient, auth_headers, sample_user
    ):
        """Test successful game creation."""
        game_data = {"difficulty_level": "medium"}

        response = client.post("/games/new", json=game_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["difficulty_level"] == "medium"
        assert data["completed"] is False
        assert "id" in data
        assert "puzzle_data" in data
        assert "current_state" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["completed_at"] is None

        # Verify puzzle structure
        puzzle = data["puzzle_data"]
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)

        # Should have some empty cells (zeros)
        empty_count = sum(row.count(0) for row in puzzle)
        assert empty_count == 45  # Medium difficulty

        # Current state should match initial puzzle
        assert data["current_state"] == data["puzzle_data"]

    def test_create_new_game_all_difficulties(self, client: TestClient, auth_headers):
        """Test game creation with all difficulty levels."""
        difficulties = {"easy": 35, "medium": 45, "hard": 55, "expert": 65}

        for difficulty, expected_empty in difficulties.items():
            game_data = {"difficulty_level": difficulty}
            response = client.post("/games/new", json=game_data, headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["difficulty_level"] == difficulty

            # Check empty cell count
            empty_count = sum(row.count(0) for row in data["puzzle_data"])
            assert empty_count == expected_empty

    def test_create_new_game_no_auth(self, client: TestClient):
        """Test game creation without authentication."""
        game_data = {"difficulty_level": "medium"}
        response = client.post("/games/new", json=game_data)

        assert response.status_code == 403

    def test_create_new_game_invalid_difficulty(self, client: TestClient, auth_headers):
        """Test game creation with invalid difficulty."""
        game_data: dict[str, str] = {"difficulty_level": "impossible"}
        response = client.post("/games/new", json=game_data, headers=auth_headers)

        # Should still create game but default to easy
        assert response.status_code == 200
        data = response.json()
        assert data["difficulty_level"] == "impossible"  # API stores whatever is sent

        # But should use easy difficulty (35 empty cells)
        empty_count = sum(row.count(0) for row in data["puzzle_data"])
        assert empty_count == 35

    def test_create_new_game_missing_difficulty(self, client: TestClient, auth_headers):
        """Test game creation without difficulty level."""
        game_data = {}
        response = client.post("/games/new", json=game_data, headers=auth_headers)

        assert response.status_code == 422  # Validation error


class TestGetUserGames:
    """Test retrieving user's games."""

    def test_get_user_games_success(
        self, client: TestClient, auth_headers, sample_game
    ):
        """Test successful retrieval of user games."""
        response = client.get("/games/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 1

        game = data[0]
        assert game["id"] == sample_game.id
        assert game["difficulty_level"] == sample_game.difficulty_level
        assert game["completed"] == sample_game.completed

    def test_get_user_games_empty(self, client: TestClient, auth_headers):
        """Test retrieving games when user has none."""
        response = client.get("/games/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_user_games_no_auth(self, client: TestClient):
        """Test retrieving games without authentication."""
        response = client.get("/games/")

        assert response.status_code == 403

    def test_get_user_games_multiple(
        self, client: TestClient, auth_headers, db_session, sample_user
    ):
        """Test retrieving multiple games."""
        # Create multiple games
        for i, difficulty in enumerate(["easy", "medium", "hard"]):
            game = Game(
                user_id=sample_user.id,
                puzzle_data="[]",
                solution="[]",
                current_state="[]",
                difficulty_level=difficulty,
                completed=(i == 0),  # First game completed
            )
            db_session.add(game)
        db_session.commit()

        response = client.get("/games/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Check that completed status is correct
        completed_games = [g for g in data if g["completed"]]
        assert len(completed_games) == 1


class TestGetSpecificGame:
    """Test retrieving a specific game."""

    def test_get_game_success(self, client: TestClient, auth_headers, sample_game):
        """Test successful retrieval of specific game."""
        response = client.get(f"/games/{sample_game.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_game.id
        assert data["difficulty_level"] == sample_game.difficulty_level
        assert data["completed"] == sample_game.completed
        assert isinstance(data["puzzle_data"], list)
        assert isinstance(data["current_state"], list)

    def test_get_game_not_found(self, client: TestClient, auth_headers):
        """Test retrieving non-existent game."""
        response = client.get("/games/99999", headers=auth_headers)

        assert response.status_code == 404
        assert "Game not found" in response.json()["detail"]

    def test_get_game_wrong_user(self, client: TestClient, auth_headers, db_session):
        """Test retrieving another user's game."""
        # Create another user and their game
        from app.models import User
        from app.core.security import get_password_hash

        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("password"),
        )
        db_session.add(other_user)
        db_session.commit()

        other_game = Game(
            user_id=other_user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="easy",
        )
        db_session.add(other_game)
        db_session.commit()

        response = client.get(f"/games/{other_game.id}", headers=auth_headers)

        assert response.status_code == 404  # Should not find other user's game

    def test_get_game_no_auth(self, client: TestClient, sample_game):
        """Test retrieving game without authentication."""
        response = client.get(f"/games/{sample_game.id}")

        assert response.status_code == 403


class TestUpdateGame:
    """Test updating game state."""

    def test_update_game_success(
        self, client: TestClient, auth_headers, sample_game, sample_sudoku_board
    ):
        """Test successful game update."""
        # Make a move on the board
        updated_board = [row[:] for row in sample_sudoku_board]  # Deep copy
        updated_board[0][2] = 4  # Place 4 at position [0,2]

        update_data = {"current_state": updated_board}

        response = client.put(
            f"/games/{sample_game.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_game.id
        assert data["current_state"] == updated_board
        assert data["completed"] is False  # Still not complete

    def test_update_game_completion(
        self, client: TestClient, auth_headers, sample_game, sample_sudoku_solution
    ):
        """Test game completion when providing complete solution."""
        update_data = {"current_state": sample_sudoku_solution}

        response = client.put(
            f"/games/{sample_game.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["completed"] is True
        assert data["completed_at"] is not None
        assert data["current_state"] == sample_sudoku_solution

    def test_update_game_not_found(
        self, client: TestClient, auth_headers, sample_sudoku_board
    ):
        """Test updating non-existent game."""
        update_data = {"current_state": sample_sudoku_board}

        response = client.put("/games/99999", json=update_data, headers=auth_headers)

        assert response.status_code == 404
        assert "Game not found" in response.json()["detail"]

    def test_update_completed_game(
        self,
        client: TestClient,
        auth_headers,
        db_session,
        sample_user,
        sample_sudoku_board,
    ):
        """Test updating already completed game."""
        # Create completed game
        completed_game = Game(
            user_id=sample_user.id,
            puzzle_data="[]",
            solution="[]",
            current_state="[]",
            difficulty_level="easy",
            completed=True,
            completed_at=datetime.utcnow(),
        )
        db_session.add(completed_game)
        db_session.commit()

        update_data = {"current_state": sample_sudoku_board}

        response = client.put(
            f"/games/{completed_game.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 400
        assert "Cannot update completed game" in response.json()["detail"]

    def test_update_game_invalid_board(
        self, client: TestClient, auth_headers, sample_game
    ):
        """Test updating game with invalid board format."""
        invalid_board = [[1, 2, 3]]  # Wrong dimensions
        update_data = {"current_state": invalid_board}

        response = client.put(
            f"/games/{sample_game.id}", json=update_data, headers=auth_headers
        )

        # Should fail during validation or processing
        assert response.status_code in [422, 500]

    def test_update_game_no_auth(
        self, client: TestClient, sample_game, sample_sudoku_board
    ):
        """Test updating game without authentication."""
        update_data = {"current_state": sample_sudoku_board}

        response = client.put(f"/games/{sample_game.id}", json=update_data)

        assert response.status_code == 403


class TestGetNextAvailableGame:
    """Test getting next available game and difficulty suggestions."""

    def test_get_next_available_with_unfinished_game(
        self, client: TestClient, auth_headers, sample_game
    ):
        """Test getting next available game when there's an unfinished game."""
        response = client.get("/games/next-available", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["has_next"] is True
        assert data["next_game_id"] == sample_game.id
        assert data["suggested_difficulty"] in ["easy", "medium", "hard", "expert"]

    def test_get_next_available_no_unfinished_games(
        self, client: TestClient, auth_headers
    ):
        """Test getting next available game when no unfinished games exist."""
        response = client.get("/games/next-available", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["has_next"] is False
        assert data["next_game_id"] is None
        assert data["suggested_difficulty"] == "easy"  # Default for new user

    def test_get_next_available_difficulty_progression(
        self, client: TestClient, auth_headers, db_session, sample_user
    ):
        """Test difficulty progression based on completed games."""
        # Create completed games to test progression
        for i in range(6):  # 6 completed games should suggest medium
            game = Game(
                user_id=sample_user.id,
                puzzle_data="[]",
                solution="[]",
                current_state="[]",
                difficulty_level="easy",
                completed=True,
                completed_at=datetime.utcnow(),
            )
            db_session.add(game)
        db_session.commit()

        response = client.get("/games/next-available", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert (
            data["suggested_difficulty"] == "medium"
        )  # 6 // 5 = 1, progression[1] = medium

    def test_get_next_available_max_difficulty(
        self, client: TestClient, auth_headers, db_session, sample_user
    ):
        """Test difficulty progression caps at expert."""
        # Create many completed games
        for i in range(20):  # Should suggest expert (max level)
            game = Game(
                user_id=sample_user.id,
                puzzle_data="[]",
                solution="[]",
                current_state="[]",
                difficulty_level="easy",
                completed=True,
                completed_at=datetime.utcnow(),
            )
            db_session.add(game)
        db_session.commit()

        response = client.get("/games/next-available", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["suggested_difficulty"] == "expert"  # Capped at max difficulty

    def test_get_next_available_no_auth(self, client: TestClient):
        """Test getting next available game without authentication."""
        response = client.get("/games/next-available")

        assert response.status_code == 403


class TestGameValidation:
    """Test game data validation and edge cases."""

    def test_game_json_serialization(
        self, client: TestClient, auth_headers, sample_game
    ):
        """Test that game data is properly serialized to/from JSON."""
        response = client.get(f"/games/{sample_game.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify JSON structure
        assert isinstance(data["puzzle_data"], list)
        assert isinstance(data["current_state"], list)

        # Verify board structure
        for board_key in ["puzzle_data", "current_state"]:
            board = data[board_key]
            assert len(board) == 9
            for row in board:
                assert len(row) == 9
                assert all(isinstance(cell, int) and 0 <= cell <= 9 for cell in row)

    def test_game_timestamps(self, client: TestClient, auth_headers):
        """Test that game timestamps are properly set."""
        game_data = {"difficulty_level": "easy"}

        response = client.post("/games/new", json=game_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify timestamps exist and are valid ISO format
        assert "created_at" in data
        assert "updated_at" in data

        # Parse timestamps to verify format
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))

        # They should be very close to current time
        now = datetime.utcnow()
        assert abs((now - created_at.replace(tzinfo=None)).total_seconds()) < 10
        assert abs((now - updated_at.replace(tzinfo=None)).total_seconds()) < 10
