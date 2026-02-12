from rich.live import Live
from rich.table import Table
from rich.text import Text

from nonogram.core import CellState, Grid, LineView
from nonogram.parser import PuzzleInput
from nonogram.solver.observer import EngineObserver


class RichObserver(EngineObserver):
    def __init__(self, puzzle: PuzzleInput, live: Live) -> None:
        self.puzzle = puzzle
        self.live = live

        self.step = 0

    def on_line_update(self, kind: str, index: int, old: LineView, new: LineView) -> None:
        self.live.update(render_grid(self.puzzle.grid))

    def on_step(self, kind: str, index: int) -> None:
        self.step += 1


def render_cell(cell: CellState) -> Text:
    """Full range of shades: █ ▓ ▒ ░
    """
    if cell == CellState.BLACK:
        return Text("██")
    if cell == CellState.WHITE:
        return Text("░░", style="grey30")
    return Text("  ")


def render_grid(grid: Grid) -> Table:
    table = Table(show_header=False, box=None, padding=(0, 0))

    for _ in range(grid.width):
        table.add_column(justify="center")

    for row in grid.cells:
        table.add_row(*[render_cell(c) for c in row])

    return table
