import json
from dataclasses import dataclass
from enum import StrEnum

from rich.live import Live
from rich.text import Text

from pixelpuzzle.exceptions import PixelValidationError


class CC(StrEnum):
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


@dataclass
class PuzzleInput:
    row_clues: list[tuple[int]]
    col_clues: list[tuple[int]]
    initial_board: list[str] | None


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
        if sum(sum(clues) for clues in row_clues) != sum(sum(clues) for clues in col_clues):
            raise PixelValidationError("Clues provided are not possible")
        board = board.split("\n") if board else None
        return PuzzleInput(row_clues, col_clues, board)

    @staticmethod
    def to_text(solver) -> str:
        row_clues = "\n".join([" ".join(map(str, row)) for row in solver.row_clues])
        col_clues = "\n".join([" ".join(map(str, col[::-1])) for col in solver.col_clues])
        board = "\n".join(solver.board)
        return "\n\n".join([row_clues, col_clues, board])


class ProgressBar:
    def __init__(self, message: str, total: int = 100) -> None:
        self.message = message
        self.length = total
        self.bar = [" "] * total
        self.live: Live | None = None

    def reset(self) -> None:
        self.bar = [" "] * self.length

    def start(self) -> None:
        self.live = Live(Text.from_ansi(str(self)), refresh_per_second=30)
        self.live.start()

    def stop(self) -> None:
        if self.live is not None:
            self.live.stop()
            self.live = None

    def __getitem__(self, index: int) -> str:
        return self.bar[index]

    def __setitem__(self, index: int, item: str) -> None:
        self.bar[index] = item
        if self.live is not None:
            self.live.update(Text.from_ansi(str(self)))

    def __str__(self) -> str:
        return f"[{''.join(self.bar)}] {self.message}"


class BoardPrinter:
    def __init__(self, row_clues: list[tuple[int]], col_clues: list[tuple[int]]):
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.rows = len(self.row_clues)
        self.cols = len(self.col_clues)
        self._form_board()

    def _form_board(self) -> None:
        board_width = self.cols + (self.cols // 5) * 5 + 1
        board_height = self.rows + self.rows // 5 + 1
        longest_row_clue = max(map(lambda clues: len(" ".join(map(str, clues))), self.row_clues))
        longest_col_clue = max(map(len, self.col_clues))
        width = longest_row_clue + 1 + board_width
        height = longest_col_clue + board_height
        self.board = [[" "] * width for _ in range(height)]
        self.board_x_offset = longest_row_clue + 2
        self.board_y_offset = longest_col_clue + 1

        # Column clues
        for i, x in enumerate(range(self.board_x_offset, width, 2)):
            for j, y in enumerate(range(self.board_y_offset - 2, -1, -1)):
                if j >= len(self.col_clues[i]):
                    break
                clue = str(self.col_clues[i][-j - 1])
                self.board[y][x] = clue[-1]
                if len(clue) == 2:
                    self.board[y][x - 1] = clue[0]

        # Row clues
        for i, (y, clues) in enumerate(zip(range(self.board_y_offset, height), self.row_clues)):
            row_clues_str = " ".join(map(str, clues))
            for x, v in zip(range(self.board_x_offset - 3, -1, -1), row_clues_str[::-1]):
                self.board[y + i // 5][x] = v

        # Empty board
        for y in range(self.board_y_offset - 1, height, 6):
            for x in range(self.board_x_offset - 1, width):
                self.board[y][x] = "-"
        for x in range(self.board_x_offset - 1, width, 10):
            for y in range(self.board_y_offset - 1, height):
                self.board[y][x] = "|"
                if y == self.board_y_offset - 1 or y == height - 1:
                    self.board[y][x] = "+"

    def merge_board(self, board: list[str], updates: list[list[bool]]) -> None:
        for i, row in enumerate(board):
            for j, cell in enumerate(row):
                cell_value = f"{CC.BOLD}{CC.GREEN}{cell}{CC.END}" if updates[i][j] else cell
                self.board[self.board_y_offset + i + i // 5][self.board_x_offset + j * 2] = (
                    cell_value
                )

    def __str__(self) -> str:
        return "\n" + "\n".join("".join(row) for row in self.board) + "\n"
