from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

from pixelpuzzle.exceptions import PixelExceptionError
from pixelpuzzle.solvers import Solver
from pixelpuzzle.solvers.utils import increment_state
from pixelpuzzle.utils import CC, Board, ProgressBar, Square


class BasicSolver(Solver):
    class SweepState:
        def __init__(
            self, outer: "BasicSolver", board: Board[Square], last_updates: list[int], hz: bool
        ):
            self.horizontal = hz
            self.outer = outer
            self.lines = ["".join(line) for line in board]
            self.last_updated = last_updates
            self.progress = ProgressBar("Rows" if hz else "Columns", len(self.lines))

        def skip_line(self, index: int) -> None:
            self.progress[index] = f"{CC.BLUE}{CC.BOLD}-{CC.END}"

        def complex_line(self, index: int) -> None:
            self.progress[index] = f"{CC.RED}{CC.BOLD}#{CC.END}"

        def increment_line(self, index: int, line: str) -> None:
            old_line = self.lines[index]
            updated = line != old_line
            self.progress[index] = f"{CC.GREEN if updated else CC.END}{CC.BOLD}#{CC.END}"
            self.lines[index] = line
            if updated:
                self.outer._update_board(index, old_line, line, self.horizontal)

        def __str__(self) -> str:
            updates = ["-" if i < self.outer.iteration else "#" for i in self.last_updated]
            return str(self.progress) + "\n" + "[" + "".join(updates) + "] Last Updated"

    def __init__(self, row_clues: list[tuple[int]], col_clues: list[tuple[int]]) -> None:
        super().__init__(row_clues, col_clues)

        self.iteration = 0
        self.last_updated_rows = [0] * self.rows
        self.last_updated_cols = [0] * self.cols
        self.complexity_base = 10**7

    def iterate(self) -> bool:
        self.recent_board_update.reset()

        state = self.SweepState(self, self.board, self.last_updated_rows, hz=True)
        self._iterate_sweep(self.row_clues, state)

        rotated = self._rotate(state.lines)
        state = self.SweepState(self, rotated, self.last_updated_cols, hz=False)
        self._iterate_sweep(self.col_clues, state)

        self.board = self._rotate(state.lines)
        self.iteration += 1

        if all(line.count(Square.BLANK) == 0 for line in self.board):
            self.completed = True
            return True

        if not any(n == self.iteration for n in self.last_updated_rows) and not any(
            n == self.iteration for n in self.last_updated_cols
        ):
            self.last_updated_rows = [self.iteration] * self.rows
            self.last_updated_cols = [self.iteration] * self.cols
            self.complexity_base *= 10
        return False

    def _update_board(self, i: int, prev: str, curr: str, hz: bool) -> None:
        def update_dir(last_updated: list[int], last_updated_perpendicular: list[int]) -> None:
            last_updated[i] = self.iteration + 1
            for j, (n, m) in enumerate(zip(prev, curr)):
                if n != m:
                    a, b = (i, j) if hz else (j, i)
                    self.recent_board_update.set(a, b)
                    last_updated_perpendicular[j] = self.iteration + 1

        if hz:
            update_dir(self.last_updated_rows, self.last_updated_cols)
        else:
            update_dir(self.last_updated_cols, self.last_updated_rows)

    def _iterate_line(self, index: int, clues: tuple[int], line: str, state: SweepState):
        state.progress[index] = "."
        if state.last_updated[index] < self.iteration:
            state.skip_line(index)
            return
        if self._is_complex(clues, line):
            state.complex_line(index)
            return
        incremented = increment_state(clues, line)
        state.increment_line(index, incremented)

    def _iterate_sweep(self, clues, state: SweepState):
        if self.verbose:
            state.progress.start()

        with ThreadPoolExecutor(max_workers=50) as tp:
            futures = [
                tp.submit(self._iterate_line, i, clue, line, state)
                for i, (clue, line) in enumerate(zip(clues, state.lines))
            ]
            for future in as_completed(futures):
                exception = future.exception()
                if isinstance(exception, PixelExceptionError):
                    raise PixelExceptionError("Failed to iterate lines", exception)

        state.progress.stop()

    def _rotate(self, lines: list[str]) -> Board[Square]:
        return Board.of(list("".join(_) for _ in zip(*lines)))

    def _is_complex(self, clues: tuple[int], state: str):
        if state.count(Square.BLANK) < 15:
            return False

        first = state.find(Square.BLANK)
        start = state[:first].count(Square.BLACK)

        reversed = state[::-1]
        last = reversed.find(Square.BLANK)
        end = reversed[:last].count(Square.BLACK)

        clues_queue = deque(clues)
        while clues_queue and clues_queue[0] <= start:
            start -= clues_queue.popleft()
        while clues_queue and clues_queue[-1] <= end:
            end -= clues_queue.pop()
        if len(clues_queue) == 0:
            return False

        length = state.count(Square.BLANK) - first - last
        remaining = length + 1 - sum(clues_queue) - len(clues_queue)
        complexity = 1
        for clue in clues_queue:
            complexity *= max(1, remaining - clue)

        complexity_limit = max(1, length * 5 * self.complexity_base)
        is_complex = complexity > 10**4 and complexity > complexity_limit
        return is_complex
