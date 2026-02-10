from enum import StrEnum
from typing import Any

from nonogram.exceptions import CellConflictContradiction, LineTooShortContradiction


class CellState(StrEnum):
    BLACK = "#"
    WHITE = "."
    UNKNOWN = " "

    @staticmethod
    def of(value: str) -> "CellState":
        if value == "#":
            return CellState.BLACK
        if value == ".":
            return CellState.WHITE
        if value == " ":
            return CellState.UNKNOWN
        raise TypeError(f"`{value}` is not a valid CellState")


class LineClue(tuple[int]):
    def __init__(self, base: Any) -> None:
        if not isinstance(base, (tuple, list)) or not all(isinstance(x, int) for x in base):
            raise TypeError("LineClue must be init as tuple[int] or list[int]")


class LineView(list[CellState]):
    def __init__(self, base: Any) -> None:
        if isinstance(base, str):
            super().__init__([CellState.of(cell) for cell in base])
        elif not isinstance(base, (tuple, list)) or not all(isinstance(x, CellState) for x in base):
            raise TypeError("LineClue must be init as tuple[CellState] or list[CellState]")
        else:
            super().__init__(base)

    def state(self) -> tuple[CellState, ...]:
        return tuple(self)

    def is_complete(self) -> bool:
        return all(cell != CellState.UNKNOWN for cell in self)

    def __str__(self) -> str:
        return "".join(str(cell) for cell in self)


class Grid:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.cells = [[CellState.UNKNOWN for _ in range(width)] for _ in range(height)]

    def row(self, i: int) -> LineView:
        return LineView(self.cells[i])

    def col(self, j: int) -> LineView:
        return LineView([self.cells[i][j] for i in range(self.height)])

    def apply_row(self, i: int, new_state: LineView) -> bool:
        if self.width != len(new_state):
            raise LineTooShortContradiction("Cannot apply states of different length")

        changed = False

        for j, val in enumerate(new_state):
            cell = self.cells[i][j]
            if cell == CellState.UNKNOWN and val != CellState.UNKNOWN:
                self.cells[i][j] = val
                changed = True
            elif val != CellState.UNKNOWN and val != cell:
                raise CellConflictContradiction(f"Cell {cell} being applied as {val}.")

        return changed

    def apply_col(self, j: int, new_state: LineView) -> bool:
        if self.height != len(new_state):
            raise LineTooShortContradiction("Cannot apply states of different length")

        changed = False

        for i, val in enumerate(new_state):
            cell = self.cells[i][j]
            if cell == CellState.UNKNOWN and val != CellState.UNKNOWN:
                self.cells[i][j] = val
                changed = True
            elif val != CellState.UNKNOWN and val != cell:
                raise CellConflictContradiction(f"Cell {cell} being applied as {val}.")

        return changed

    def is_solved(self) -> bool:
        return all(cell != CellState.UNKNOWN for row in self.cells for cell in row)

    def copy(self) -> "Grid":
        g = Grid(self.width, self.height)
        g.cells = [row[:] for row in self.cells]
        return g
