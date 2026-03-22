from collections import deque
from dataclasses import dataclass

from nonogram.core import Cell, Clues, Grid
from nonogram.exceptions import Contradiction
from nonogram.main import make_line_solver
from nonogram.parser import PuzzleInput
from nonogram.rules.enumeration_rules import EnumerationRule


@dataclass
class StepResult:
    kind: str  # "row", "col", or "repopulate"
    index: int  # -1 when kind == "repopulate"
    changed: bool
    is_done: bool
    is_stuck: bool
    error: str | None = None
    updated_cells: set[tuple[int, int]] | None = None


class StepwiseSolver:
    def __init__(self, puzzle: PuzzleInput) -> None:
        self.puzzle = puzzle
        self.grid = puzzle.grid.copy()
        self._line_solver = make_line_solver()
        self.queue: deque[tuple[str, int]] = deque(
            [("row", i) for i in range(puzzle.height)] + [("col", j) for j in range(puzzle.width)]
        )
        self._history: deque[tuple[Grid, deque[tuple[str, int]]]] = deque(maxlen=50)
        self._changed_since_repopulation: bool = False
        self._stuck = False

    @property
    def can_undo(self) -> bool:
        return len(self._history) > 0

    @property
    def is_done(self) -> bool:
        return self.grid.is_solved()

    @property
    def is_stuck(self) -> bool:
        return self._stuck

    @property
    def queue_length(self) -> int:
        return len(self.queue)

    def step(self) -> StepResult | None:
        """Process one queue item. Returns None if stuck (no progress possible)."""
        if self._stuck:
            return None

        # Queue is empty — decide whether to repopulate or declare stuck
        if not self.queue:
            if self.grid.is_solved():
                return None
            if not self._changed_since_repopulation:
                self._stuck = True
                return None
            # Repopulate with all rows and cols
            self._history.append((self.grid.copy(), deque(self.queue)))
            self.queue = deque(
                [("row", i) for i in range(self.puzzle.height)]
                + [("col", j) for j in range(self.puzzle.width)]
            )
            self._changed_since_repopulation = False
            return StepResult(
                kind="repopulate", index=-1, changed=False, is_done=False, is_stuck=False
            )

        # Save state for undo before processing
        self._history.append((self.grid.copy(), deque(self.queue)))

        kind, index = self.queue.popleft()
        clues: Clues = (
            self.puzzle.row_clues[index] if kind == "row" else self.puzzle.col_clues[index]
        )
        line = self.grid.row(index) if kind == "row" else self.grid.col(index)

        try:
            new_line = self._line_solver.solve(clues, line)
            changed = (
                self.grid.apply_row(index, new_line)
                if kind == "row"
                else self.grid.apply_col(index, new_line)
            )
        except Contradiction as exc:
            self._stuck = True
            return StepResult(
                kind=kind,
                index=index,
                changed=False,
                is_done=False,
                is_stuck=True,
                error=f"Contradiction on {kind} {index}: {exc}",
            )

        updated_cells: set[tuple[int, int]] = set()
        if changed:
            self._changed_since_repopulation = True
            updated_indices = [i for i, (old, new) in enumerate(zip(line, new_line)) if old != new]
            for updated_i in updated_indices:
                if kind == "row":
                    updated_cells.add((index, updated_i))
                else:
                    updated_cells.add((updated_i, index))
                new_kind = "col" if kind == "row" else "row"
                if (new_kind, updated_i) in self.queue:
                    self.queue.remove((new_kind, updated_i))
                self.queue.appendleft((new_kind, updated_i))

        return StepResult(
            kind=kind,
            index=index,
            changed=changed,
            is_done=self.grid.is_solved(),
            is_stuck=False,
            updated_cells=updated_cells if updated_cells else None,
        )

    def undo(self) -> bool:
        """Restore the state before the last step. Returns False if nothing to undo."""
        if not self._history:
            return False
        self.grid, self.queue = self._history.pop()
        self._stuck = False
        return True

    def reset(self) -> None:
        """Clear the grid to all-unknown and restart the queue."""
        self.grid = Grid(self.puzzle.width, self.puzzle.height)
        self.queue = deque(
            [("row", i) for i in range(self.puzzle.height)]
            + [("col", j) for j in range(self.puzzle.width)]
        )
        self._history.clear()
        self._changed_since_repopulation = False
        self._stuck = False

    @property
    def enumeration_enabled(self) -> bool:
        return any(isinstance(r, EnumerationRule) for r in self._line_solver.rules)

    def toggle_enumeration(self) -> bool:
        """Toggle the enumeration rule on/off. Returns the new state (True=enabled)."""
        rules = self._line_solver.rules
        if self.enumeration_enabled:
            self._line_solver.rules = [r for r in rules if not isinstance(r, EnumerationRule)]
            return False
        else:
            self._stuck = False
            self._changed_since_repopulation = True
            rules.append(EnumerationRule())
            return True

    def set_cell(self, row: int, col: int, value: Cell) -> None:
        """Manually set a cell and re-queue the affected row and column."""
        self.grid.cells[row][col] = value
        self._stuck = False
        self._changed_since_repopulation = True
        if ("row", row) not in self.queue:
            self.queue.append(("row", row))
        if ("col", col) not in self.queue:
            self.queue.append(("col", col))
