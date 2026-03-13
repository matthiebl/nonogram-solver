from collections import deque
from dataclasses import dataclass

from nonogram.core import Cell, Clues, Grid
from nonogram.parser import PuzzleInput
from nonogram.rules.edge_rules import GlueEdgeRule, MercuryEdgeRule
from nonogram.rules.overlap_rules import (
    ClueOrderingConstraintRule,
    ForcedSeparationRule,
    MinimumLengthExpansionRule,
    NeverBlackRule,
    OverlapRule,
    RunCappingRule,
    UniqueAssignmentRule,
)
from nonogram.rules.simple_rules import CompleteCluesRule, FirstClueGapRule, GapTooSmallRule
from nonogram.rules.split_rules import CompleteEdgeSplitRule
from nonogram.solver.split_line_solver import SplitLineSolver


@dataclass
class StepResult:
    kind: str  # "row", "col", or "repopulate"
    index: int  # -1 when kind == "repopulate"
    changed: bool
    is_done: bool
    is_stuck: bool


def make_line_solver() -> SplitLineSolver:
    """Build the full rule pipeline including EnumerationRule as fallback."""
    return SplitLineSolver(
        rules=[
            CompleteCluesRule(),
            OverlapRule(),
            GlueEdgeRule(),
            MercuryEdgeRule(),
            FirstClueGapRule(),
            MinimumLengthExpansionRule(),
            RunCappingRule(),
            ForcedSeparationRule(),
            UniqueAssignmentRule(),
            ClueOrderingConstraintRule(),
            NeverBlackRule(),
            GapTooSmallRule(),
            CompleteCluesRule(),
        ],
        split_rules=[
            CompleteEdgeSplitRule(),
        ],
    )


class StepwiseSolver:
    def __init__(self, puzzle: PuzzleInput) -> None:
        self.puzzle = puzzle
        self.grid = puzzle.grid.copy()
        self._line_solver = make_line_solver()
        self.queue: deque[tuple[str, int]] = deque(
            [("row", i) for i in range(puzzle.height)] + [("col", j) for j in range(puzzle.width)]
        )
        self._prev_state: tuple[Grid, deque[tuple[str, int]]] | None = None
        self._changed_since_repopulation: bool = False
        self._stuck = False

    @property
    def can_undo(self) -> bool:
        return self._prev_state is not None

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
            self._prev_state = (self.grid.copy(), deque(self.queue))
            self.queue = deque(
                [("row", i) for i in range(self.puzzle.height)]
                + [("col", j) for j in range(self.puzzle.width)]
            )
            self._changed_since_repopulation = False
            return StepResult(
                kind="repopulate", index=-1, changed=False, is_done=False, is_stuck=False
            )

        # Save state for undo before processing
        self._prev_state = (self.grid.copy(), deque(self.queue))

        kind, index = self.queue.popleft()
        clues: Clues = (
            self.puzzle.row_clues[index] if kind == "row" else self.puzzle.col_clues[index]
        )
        line = self.grid.row(index) if kind == "row" else self.grid.col(index)

        new_line = self._line_solver.solve(clues, line)
        changed = (
            self.grid.apply_row(index, new_line)
            if kind == "row"
            else self.grid.apply_col(index, new_line)
        )

        if changed:
            self._changed_since_repopulation = True
            updated_indices = [i for i, (old, new) in enumerate(zip(line, new_line)) if old != new]
            for updated_i in updated_indices:
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
        )

    def undo(self) -> bool:
        """Restore the state before the last step. Returns False if nothing to undo."""
        if self._prev_state is None:
            return False
        self.grid, self.queue = self._prev_state
        self._prev_state = None
        self._stuck = False
        return True

    def reset(self) -> None:
        """Clear the grid to all-unknown and restart the queue."""
        self.grid = Grid(self.puzzle.width, self.puzzle.height)
        self.queue = deque(
            [("row", i) for i in range(self.puzzle.height)]
            + [("col", j) for j in range(self.puzzle.width)]
        )
        self._prev_state = None
        self._changed_since_repopulation = False
        self._stuck = False

    def set_cell(self, row: int, col: int, value: Cell) -> None:
        """Manually set a cell and re-queue the affected row and column."""
        self.grid.cells[row][col] = value
        self._stuck = False
        self._changed_since_repopulation = True
        if ("row", row) not in self.queue:
            self.queue.append(("row", row))
        if ("col", col) not in self.queue:
            self.queue.append(("col", col))
