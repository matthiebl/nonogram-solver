from enum import StrEnum
from typing import Any

from nonogram.exceptions import CellConflictContradiction, LineTooShortContradiction


class Cell(StrEnum):
    BOX = "#"
    CROSS = "."
    UNKNOWN = " "

    @staticmethod
    def of(value: str) -> "Cell":
        if value == "#":
            return Cell.BOX
        if value == ".":
            return Cell.CROSS
        if value == " ":
            return Cell.UNKNOWN
        raise TypeError(f"`{value}` is not a valid Cell")


class Clues(tuple[int]):
    def __init__(self, base: Any) -> None:
        if not isinstance(base, (tuple, list)) or not all(isinstance(x, int) for x in base):
            raise TypeError(f"Clues must be init as tuple[int] or list[int]: {base}")

    def __str__(self) -> str:
        return " ".join(str(clue) for clue in self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join(map(str, self))})"


class LineState(list[Cell]):
    def __init__(self, base: Any) -> None:
        if isinstance(base, str):
            super().__init__([Cell.of(cell) for cell in base])
        elif not isinstance(base, (tuple, list)) or not all(isinstance(x, Cell) for x in base):
            raise TypeError(
                f"LineState must be init as tuple[CellState] or list[CellState]: {base}"
            )
        else:
            super().__init__(base)

    def state(self) -> tuple[Cell, ...]:
        return tuple(self)

    def is_complete(self) -> bool:
        return all(cell != Cell.UNKNOWN for cell in self)

    def __str__(self) -> str:
        return "".join(str(cell) for cell in self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self})"

    def __hash__(self) -> int:  # type: ignore[override]
        return hash(str(self))


class Grid:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.cells = [[Cell.UNKNOWN for _ in range(width)] for _ in range(height)]

    def row(self, i: int) -> LineState:
        return LineState(self.cells[i])

    def col(self, j: int) -> LineState:
        return LineState([self.cells[i][j] for i in range(self.height)])

    def apply_row(self, i: int, new_state: LineState) -> bool:
        if self.width != len(new_state):
            raise LineTooShortContradiction("Cannot apply states of different length")

        changed = False

        for j, val in enumerate(new_state):
            cell = self.cells[i][j]
            if cell == Cell.UNKNOWN and val != Cell.UNKNOWN:
                self.cells[i][j] = val
                changed = True
            elif val != Cell.UNKNOWN and val != cell:
                raise CellConflictContradiction(f"Cell {cell} being applied as {val}.")

        return changed

    def apply_col(self, j: int, new_state: LineState) -> bool:
        if self.height != len(new_state):
            raise LineTooShortContradiction("Cannot apply states of different length")

        changed = False

        for i, val in enumerate(new_state):
            cell = self.cells[i][j]
            if cell == Cell.UNKNOWN and val != Cell.UNKNOWN:
                self.cells[i][j] = val
                changed = True
            elif val != Cell.UNKNOWN and val != cell:
                raise CellConflictContradiction(f"Cell {cell} being applied as {val}.")

        return changed

    def is_solved(self) -> bool:
        return all(cell != Cell.UNKNOWN for row in self.cells for cell in row)

    def copy(self) -> "Grid":
        g = Grid(self.width, self.height)
        g.cells = [row[:] for row in self.cells]
        return g
