import random
import json
from typing import List, Tuple


class SudokuGenerator:
    def __init__(self):
        self.size = 9
        self.box_size = 3

    def is_valid(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        for x in range(9):
            if board[row][x] == num or board[x][col] == num:
                return False

        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
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
        board = [[0 for _ in range(9)] for _ in range(9)]

        for i in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for row in range(3):
                for col in range(3):
                    board[i + row][i + col] = nums[row * 3 + col]

        self.solve_sudoku(board)
        return board

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
        solution = self.generate_complete_sudoku()
        puzzle = self.remove_numbers(solution, difficulty)
        return puzzle, solution

    def is_complete(self, board: List[List[int]]) -> bool:
        for row in board:
            for cell in row:
                if cell == 0:
                    return False

        for i in range(9):
            for j in range(9):
                num = board[i][j]
                board[i][j] = 0
                if not self.is_valid(board, i, j, num):
                    board[i][j] = num
                    return False
                board[i][j] = num
        return True

    def validate_move(
        self, board: List[List[int]], row: int, col: int, num: int
    ) -> bool:
        if row < 0 or row >= 9 or col < 0 or col >= 9:
            return False
        if num < 1 or num > 9:
            return False
        return self.is_valid(board, row, col, num)


def board_to_json(board: List[List[int]]) -> str:
    return json.dumps(board)


def json_to_board(json_str: str) -> List[List[int]]:
    return json.loads(json_str)


sudoku_generator = SudokuGenerator()
