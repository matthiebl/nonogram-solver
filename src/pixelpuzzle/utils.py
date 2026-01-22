import json
from enum import StrEnum

from pixelpuzzle.solvers import PuzzleInput


class CC(StrEnum):
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


class InputParser:
    @staticmethod
    def parse(file_path: str) -> PuzzleInput:
        with open(file_path) as file:
            if file_path.endswith(".pix.json"):
                content = json.load(file)
                print(content)
                raise NotImplementedError("JSON schema validator not implemented")
            else:
                return InputParser.parse_text(file.read())

    @staticmethod
    def parse_text(content: str) -> PuzzleInput:
        [row_clues, col_clues, board] = content.split("\n\n")
        row_clues = [tuple(map(int, line.split())) for line in row_clues.split("\n")]
        col_clues = [tuple(list(map(int, line.split()))[::-1]) for line in col_clues.split("\n")]
        board = board.split("\n") if board else None
        return PuzzleInput(row_clues, col_clues, board)


class ProgressBar:
    def __init__(self, message: str, total: int = 100) -> None:
        self.message = message
        self.length = total
        self.bar = [" "] * total

    def reset(self) -> None:
        self.bar = [" "] * self.length

    def __getitem__(self, index: int) -> str:
        return self.bar[index]

    def __setitem__(self, index: int, item: str) -> None:
        self.bar[index] = item

    def __str__(self) -> str:
        return f"[{''.join(self.bar)}] {self.message}"
