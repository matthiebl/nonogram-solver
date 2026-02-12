import time

from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from nonogram.core import CellState, Grid, LineView
from nonogram.parser import PuzzleInput
from nonogram.solver.observer import EngineObserver


class RichObserver(EngineObserver):
    def __init__(self, puzzle: PuzzleInput, live: Live) -> None:
        self.start = time.time()
        self.rows = 0
        self.cols = 0

        self.puzzle = puzzle
        self.live = live

        self.layout = Layout()
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="grid", ratio=1),
            Layout(name="footer", size=3),
        )
        self.layout["header"].split_row(
            Layout(name="title"),
            Layout(name="progress"),
        )
        self.layout["title"].update(Panel(Text("Solving " + puzzle.meta.get("title", "Nonogram"))))
        self.layout["progress"].update(Panel(Align(Text("Progress"), align="right"), expand=True))
        self.layout["grid"].update(
            Align(render_grid(puzzle.grid), align="center", vertical="middle")
        )

    def on_update(self) -> None:
        complete, total, percentage = get_grid_stats(self.puzzle.grid)
        elapsed = time.time() - self.start
        time_str = f"{int(elapsed // 60):02d}:{elapsed % 60:02.3f}"
        self.layout["progress"].update(
            Panel(
                Align(
                    f"{time_str} - {complete}/{total} - {percentage}%",
                    align="right",
                ),
                expand=True,
            )
        )
        self.live.update(self.layout)

    def on_line_update(self, kind: str, index: int, old: LineView, new: LineView) -> None:
        self.layout["grid"].update(
            Align(render_grid(self.puzzle.grid), align="center", vertical="middle")
        )
        self.on_update()

    def on_step(self, kind: str, index: int) -> None:
        if kind == "row":
            self.rows += 1
        else:
            self.cols += 1
        self.layout["footer"].update(
            Panel(
                Text(
                    f"Processed: {self.rows} rows, {self.cols} "
                    + f"columns. Looking at {kind} {index + 1}..."
                )
            )
        )
        self.on_update()


def render_cell(cell: CellState) -> Text:
    """Full range of shades: █ ▓ ▒ ░"""
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


def get_grid_stats(grid: Grid) -> tuple[int, int, int]:
    complete = sum(cell != CellState.UNKNOWN for row in grid.cells for cell in row)
    total = grid.width * grid.height
    return complete, total, round(complete / total * 100, 1)
