from dataclasses import dataclass
from enum import StrEnum


class Square(StrEnum):
    BLANK = " "
    WHITE = "."
    BLACK = "#"


class BoardUpdate:
    def __init__(self, rows: int, cols: int) -> None:
        self.rows = rows
        self.cols = cols
        self.board = [[False] * self.cols for _ in range(self.rows)]

    def reset(self) -> None:
        self.board = [[False] * self.cols for _ in range(self.rows)]

    def set(self, r: int, c: int, value: bool = True) -> None:
        self.board[r][c] = value


@dataclass
class PuzzleInput:
    row_clues: list[tuple[int]]
    col_clues: list[tuple[int]]
    initial_board: list[str] | None


class Solver:
    def __init__(self, row_clues: list[tuple[int]], col_clues: list[tuple[int]]):
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.rows = len(self.row_clues)
        self.cols = len(self.col_clues)

        self.board = [Square.BLANK * self.cols for _ in range(self.rows)]

        self.completed = False

    @classmethod
    def of(cls, puzzle: PuzzleInput) -> "Solver":
        solver: Solver = cls(puzzle.row_clues, puzzle.col_clues)
        if puzzle.initial_board:
            solver.board = puzzle.initial_board
        return solver

    def iterate(self) -> None:
        raise NotImplementedError("Solver.iterate")

    def __str__(self) -> str:
        result = "\n"
        for i, row in enumerate(self.board):
            if i % 5 == 0:
                result += ("+" + "---------+" * (len(row) // 5)) + "\n"
            for j, cell in enumerate(row):
                if j % 5 == 0:
                    result += "|"
                if self.recent_board_update.board[i][j]:
                    result += f"\033[1;32m{cell}\033[0m"
                else:
                    result += cell
                if (j + 1) % 5 != 0:
                    result += " "
            result += "| " + " ".join(map(str, self.row_clues[i])) + "\n"

        result += "+" + "---------+" * (len(row) // 5) + "\n"

        longest_col_clue = max(len(col) for col in self.col_clues)
        clues = [list(col) + [" "] * (longest_col_clue - len(col)) for col in self.col_clues]
        for nums in zip(*clues):
            result += "".join(f"{n:>2}" for n in nums) + "\n"

        return result
