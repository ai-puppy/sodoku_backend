import pytest
import json

from app.core.sudoku import (
    SudokuGenerator,
    sudoku_generator,
    board_to_json,
    json_to_board,
)


class TestSudokuGenerator:
    """Test the SudokuGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create a SudokuGenerator instance."""
        return SudokuGenerator()

    def test_is_valid_correct_placement(self, generator, sample_sudoku_board):
        """Test valid number placement."""
        # Try placing 2 at position [0, 2] (valid placement)
        assert generator.is_valid(sample_sudoku_board, 0, 2, 2) is True

    def test_is_valid_row_conflict(self, generator, sample_sudoku_board):
        """Test invalid placement due to row conflict."""
        # Try placing 5 at position [0, 2] (5 already exists in row 0)
        assert generator.is_valid(sample_sudoku_board, 0, 2, 5) is False

    def test_is_valid_column_conflict(self, generator, sample_sudoku_board):
        """Test invalid placement due to column conflict."""
        # Try placing 6 at position [0, 0] (6 exists in column 0)
        assert generator.is_valid(sample_sudoku_board, 0, 0, 6) is False

    def test_is_valid_box_conflict(self, generator, sample_sudoku_board):
        """Test invalid placement due to 3x3 box conflict."""
        # Try placing 9 at position [0, 0] (9 exists in same 3x3 box)
        assert generator.is_valid(sample_sudoku_board, 0, 0, 9) is False

    def test_solve_sudoku_valid_board(self, generator, sample_sudoku_board):
        """Test solving a valid Sudoku puzzle."""
        board_copy = [row[:] for row in sample_sudoku_board]  # Deep copy
        result = generator.solve_sudoku(board_copy)

        assert result is True
        # Verify no zeros remain
        for row in board_copy:
            assert 0 not in row
        # Verify it's a valid solution
        assert generator.is_complete(board_copy) is True

    def test_solve_sudoku_impossible_board(self, generator):
        """Test solving an impossible Sudoku puzzle."""
        # Create an impossible board (two 1s in first row)
        impossible_board = [
            [1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

        result = generator.solve_sudoku(impossible_board)
        assert result is False

    def test_generate_complete_sudoku(self, generator):
        """Test generation of a complete Sudoku solution."""
        board = generator.generate_complete_sudoku()

        # Check board dimensions
        assert len(board) == 9
        assert all(len(row) == 9 for row in board)

        # Check all cells are filled (no zeros)
        for row in board:
            assert 0 not in row
            assert all(1 <= cell <= 9 for cell in row)

        # Verify it's a valid solution
        assert generator.is_complete(board) is True

    def test_remove_numbers_difficulty_levels(self, generator):
        """Test number removal for different difficulty levels."""
        complete_board = generator.generate_complete_sudoku()

        difficulties = ["easy", "medium", "hard", "expert"]
        expected_removed = [35, 45, 55, 65]

        for difficulty, expected in zip(difficulties, expected_removed):
            puzzle = generator.remove_numbers(complete_board, difficulty)

            # Count empty cells (zeros)
            empty_count = sum(row.count(0) for row in puzzle)
            assert empty_count == expected

    def test_remove_numbers_invalid_difficulty(self, generator):
        """Test number removal with invalid difficulty defaults to easy."""
        complete_board = generator.generate_complete_sudoku()
        puzzle = generator.remove_numbers(complete_board, "invalid")

        # Should default to easy (35 removed)
        empty_count = sum(row.count(0) for row in puzzle)
        assert empty_count == 35

    def test_generate_puzzle(self, generator):
        """Test complete puzzle generation."""
        puzzle, solution = generator.generate_puzzle("medium")

        # Check dimensions
        assert len(puzzle) == 9 and len(solution) == 9
        assert all(len(row) == 9 for row in puzzle)
        assert all(len(row) == 9 for row in solution)

        # Solution should be complete
        assert generator.is_complete(solution) is True

        # Puzzle should have empty cells
        empty_count = sum(row.count(0) for row in puzzle)
        assert empty_count == 45  # Medium difficulty

        # All non-zero cells in puzzle should match solution
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    assert puzzle[i][j] == solution[i][j]

    def test_is_complete_valid_solution(self, generator, sample_sudoku_solution):
        """Test completion check with valid solution."""
        assert generator.is_complete(sample_sudoku_solution) is True

    def test_is_complete_incomplete_board(self, generator, sample_sudoku_board):
        """Test completion check with incomplete board."""
        assert generator.is_complete(sample_sudoku_board) is False

    def test_is_complete_invalid_solution(self, generator):
        """Test completion check with invalid completed board."""
        invalid_complete = [
            [1, 1, 3, 4, 5, 6, 7, 8, 9],  # Two 1s in first row
            [4, 5, 6, 7, 8, 9, 1, 2, 3],
            [7, 8, 9, 1, 2, 3, 4, 5, 6],
            [2, 3, 4, 5, 6, 7, 8, 9, 1],
            [5, 6, 7, 8, 9, 1, 2, 3, 4],
            [8, 9, 1, 2, 3, 4, 5, 6, 7],
            [3, 4, 5, 6, 7, 8, 9, 1, 2],
            [6, 7, 8, 9, 1, 2, 3, 4, 5],
            [9, 2, 2, 3, 4, 5, 6, 7, 8],
        ]

        assert generator.is_complete(invalid_complete) is False

    def test_validate_move_valid(self, generator, sample_sudoku_board):
        """Test valid move validation."""
        assert generator.validate_move(sample_sudoku_board, 0, 2, 2) is True

    def test_validate_move_invalid_position(self, generator, sample_sudoku_board):
        """Test move validation with invalid position."""
        assert generator.validate_move(sample_sudoku_board, -1, 0, 1) is False
        assert generator.validate_move(sample_sudoku_board, 9, 0, 1) is False
        assert generator.validate_move(sample_sudoku_board, 0, -1, 1) is False
        assert generator.validate_move(sample_sudoku_board, 0, 9, 1) is False

    def test_validate_move_invalid_number(self, generator, sample_sudoku_board):
        """Test move validation with invalid number."""
        assert generator.validate_move(sample_sudoku_board, 0, 2, 0) is False
        assert generator.validate_move(sample_sudoku_board, 0, 2, 10) is False

    def test_validate_move_conflict(self, generator, sample_sudoku_board):
        """Test move validation with conflicting number."""
        assert (
            generator.validate_move(sample_sudoku_board, 0, 2, 5) is False
        )  # 5 exists in row


class TestSudokuUtilities:
    """Test utility functions for board serialization."""

    def test_board_to_json(self, sample_sudoku_board):
        """Test board serialization to JSON."""
        json_str = board_to_json(sample_sudoku_board)

        assert isinstance(json_str, str)
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed == sample_sudoku_board

    def test_json_to_board(self, sample_sudoku_board):
        """Test board deserialization from JSON."""
        json_str = board_to_json(sample_sudoku_board)
        board = json_to_board(json_str)

        assert board == sample_sudoku_board
        assert isinstance(board, list)
        assert len(board) == 9
        assert all(len(row) == 9 for row in board)

    def test_json_roundtrip(self, sample_sudoku_board):
        """Test JSON serialization roundtrip."""
        json_str = board_to_json(sample_sudoku_board)
        board = json_to_board(json_str)
        json_str2 = board_to_json(board)

        assert json_str == json_str2
        assert board == sample_sudoku_board


class TestSudokuGeneratorInstance:
    """Test the global sudoku_generator instance."""

    def test_sudoku_generator_instance(self):
        """Test that the global instance works correctly."""
        assert isinstance(sudoku_generator, SudokuGenerator)

        # Test it can generate puzzles
        puzzle, solution = sudoku_generator.generate_puzzle("easy")
        assert len(puzzle) == 9
        assert len(solution) == 9
        assert sudoku_generator.is_complete(solution) is True


class TestSudokuValidation:
    """Test validation methods."""

    @pytest.fixture
    def generator(self):
        """Create a SudokuGenerator instance."""
        return SudokuGenerator()

    def test_is_valid_board_with_valid_complete_board(
        self, generator, sample_sudoku_solution
    ):
        """Test is_valid_board with a valid complete board."""
        assert generator.is_valid_board(sample_sudoku_solution) is True

    def test_is_valid_board_with_invalid_board(self, generator):
        """Test is_valid_board with an invalid board."""
        invalid_board = [
            [1, 1, 3, 4, 5, 6, 7, 8, 9],  # Two 1s in first row
            [4, 5, 6, 7, 8, 9, 1, 2, 3],
            [7, 8, 9, 1, 2, 3, 4, 5, 6],
            [2, 3, 4, 5, 6, 7, 8, 9, 1],
            [5, 6, 7, 8, 9, 1, 2, 3, 4],
            [8, 9, 1, 2, 3, 4, 5, 6, 7],
            [3, 4, 5, 6, 7, 8, 9, 1, 2],
            [6, 7, 8, 9, 1, 2, 3, 4, 5],
            [9, 2, 2, 3, 4, 5, 6, 7, 8],
        ]
        assert generator.is_valid_board(invalid_board) is False

    def test_generate_puzzle_is_solvable(self, generator):
        """Test that generated puzzles are solvable."""
        for difficulty in ["easy", "medium", "hard", "expert"]:
            puzzle, solution = generator.generate_puzzle(difficulty)

            # Test that puzzle can be solved
            puzzle_copy = [row[:] for row in puzzle]
            assert generator.solve_sudoku(puzzle_copy) is True

            # Test that solution is complete and valid
            assert generator.is_complete(solution) is True
            assert generator.is_valid_board(solution) is True


class TestSudokuEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_board_solving(self):
        """Test solving completely empty board."""
        generator = SudokuGenerator()
        empty_board = [[0 for _ in range(9)] for _ in range(9)]

        result = generator.solve_sudoku(empty_board)
        assert result is True
        assert generator.is_complete(empty_board) is True

    def test_nearly_complete_board(self):
        """Test solving board with only one empty cell."""
        generator = SudokuGenerator()
        nearly_complete = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 0],  # Missing 9
        ]

        result = generator.solve_sudoku(nearly_complete)
        assert result is True
        assert nearly_complete[8][8] == 9
