import random
import json
from typing import List, Tuple


class SudokuGenerator:
    def __init__(self):
        self.size = 9
        self.box_size = 3

    def is_valid(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        # Check row, column, and 3x3 box in one loop
        for i in range(9):
            # Check row and column
            if board[row][i] == num or board[i][col] == num:
                return False
            # Check 3x3 box
            box_row = 3 * (row // 3) + i // 3
            box_col = 3 * (col // 3) + i % 3
            if board[box_row][box_col] == num:
                return False
        return True

    def solve_sudoku(self, board: List[List[int]]) -> bool:
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    for num in range(1, 10):
                        if self.is_valid(board, i, j, num):
                            board[i][j] = num
                            if self.solve_sudoku(board):
                                return True
                            board[i][j] = 0
                    return False
        return True

    def generate_complete_sudoku(self) -> List[List[int]]:
        """Generate a complete valid Sudoku board using randomized backtracking."""
        board = [[0 for _ in range(9)] for _ in range(9)]

        # Use randomized backtracking to generate a complete valid board
        self._fill_board_randomly(board)
        return board

    def _fill_board_randomly(self, board: List[List[int]]) -> bool:
        """Fill the board using randomized backtracking."""
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    # Create a randomized list of numbers to try
                    numbers = list(range(1, 10))
                    random.shuffle(numbers)

                    for num in numbers:
                        if self.is_valid(board, i, j, num):
                            board[i][j] = num
                            if self._fill_board_randomly(board):
                                return True
                            board[i][j] = 0
                    return False
        return True

    def remove_numbers(
        self, board: List[List[int]], difficulty: str
    ) -> List[List[int]]:
        difficulty_levels = {"easy": 35, "medium": 45, "hard": 55, "expert": 65}

        cells_to_remove = difficulty_levels.get(difficulty, 35)
        puzzle = [row[:] for row in board]

        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)

        for i, (row, col) in enumerate(positions):
            if i >= cells_to_remove:
                break
            puzzle[row][col] = 0

        return puzzle

    def generate_puzzle(
        self, difficulty: str = "medium"
    ) -> Tuple[List[List[int]], List[List[int]]]:
        """Generate a valid Sudoku puzzle."""
        # Generate a complete valid solution
        solution = self.generate_complete_sudoku()

        # Create puzzle by removing numbers
        puzzle = self.remove_numbers(solution, difficulty)

        # Verify puzzle is solvable
        puzzle_copy = [row[:] for row in puzzle]
        if not self.solve_sudoku(puzzle_copy):
            # If puzzle is not solvable, try again
            return self.generate_puzzle(difficulty)

        return puzzle, solution

    def is_complete(self, board: List[List[int]]) -> bool:
        """Check if a board is completely filled and valid."""
        # First check if all cells are filled
        for row in board:
            for cell in row:
                if cell == 0:
                    return False

        # Then check if the board is valid
        return self.is_valid_board(board)

    def validate_move(
        self, board: List[List[int]], row: int, col: int, num: int
    ) -> bool:
        if row < 0 or row >= 9 or col < 0 or col >= 9:
            return False
        if num < 1 or num > 9:
            return False
        return self.is_valid(board, row, col, num)

    def is_valid_board(self, board: List[List[int]]) -> bool:
        """Check if a board follows Sudoku rules (no conflicts)."""
        for i in range(9):
            for j in range(9):
                if board[i][j] != 0:
                    # Temporarily remove the number and check if it's valid to place
                    num = board[i][j]
                    board[i][j] = 0
                    is_valid = self.is_valid(board, i, j, num)
                    board[i][j] = num
                    if not is_valid:
                        return False
        return True


def board_to_json(board: List[List[int]]) -> str:
    return json.dumps(board)


def json_to_board(json_str: str) -> List[List[int]]:
    return json.loads(json_str)


sudoku_generator = SudokuGenerator()
