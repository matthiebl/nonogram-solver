from pixelpuzzle.utils import Board, BoardPrinter, PuzzleInput, Square


class BoardUpdate:
    def __init__(self, rows: int, cols: int) -> None:
        self.rows = rows
        self.cols = cols
        self.board = [[False] * self.cols for _ in range(self.rows)]

    def reset(self) -> None:
        self.board = [[False] * self.cols for _ in range(self.rows)]

    def set(self, r: int, c: int, value: bool = True) -> None:
        self.board[r][c] = value


class Solver:
    def __init__(self, row_clues: list[tuple[int]], col_clues: list[tuple[int]]):
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.rows = len(self.row_clues)
        self.cols = len(self.col_clues)

        self.board = Board(self.rows, self.cols, default=Square.BLANK)
        self.recent_board_update = BoardUpdate(self.rows, self.cols)
        self.pretty_board = BoardPrinter(self.row_clues, self.col_clues)

        self.completed = False
        self.verbose = False

    @classmethod
    def of(cls, puzzle: PuzzleInput) -> "Solver":
        solver: Solver = cls(puzzle.row_clues, puzzle.col_clues)
        if puzzle.initial_board is not None:
            solver.board = puzzle.initial_board
        return solver

    def set_verbosity(self, verbose: bool) -> None:
        self.verbose = verbose

    def iterate(self) -> None:
        raise NotImplementedError("Solver.iterate")

    def __str__(self) -> str:
        self.pretty_board.merge_board(self.board, self.recent_board_update.board)
        return str(self.pretty_board)
