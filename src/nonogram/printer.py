import time
from typing import Any

from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from nonogram.core import CellState, Grid, LineClue, LineView
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
        self.layout["grid"].update(Align(render_grid(puzzle), align="center", vertical="middle"))

    def on_update(self) -> None:
        complete, total, percentage = get_grid_stats(self.puzzle.grid)
        elapsed = time.time() - self.start
        time_str = (
            f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}.{int(elapsed * 1000 % 1000):03d}"
        )
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
            Align(render_grid(self.puzzle), align="center", vertical="middle")
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
        return Text("░░", style="grey50")
    return Text("  ")


def render_grid(puzzle: PuzzleInput, image_only: bool = False) -> Table:
    table = Table(show_header=False, box=None, padding=(0, 0))

    table_width = puzzle.width + (0 if image_only else puzzle.width // 5 + 1)
    for _ in range(table_width):
        table.add_column(justify="center")

    if image_only:
        for row in puzzle.grid.cells:
            table.add_row(*render_row(None, row))
    else:
        for line in render_column_clues(puzzle.col_clues):
            table.add_row(*line)

        table.add_row(*render_blank_row(puzzle.width))
        for i, (clues, row) in enumerate(zip(puzzle.row_clues, puzzle.grid.cells), start=1):
            table.add_row(*render_row(clues, row))
            if i % 5 == 0:
                table.add_row(*render_blank_row(puzzle.width))

    return table


def render_row(clues: LineClue | None, row: list[CellState]) -> list[Any]:
    if clues is None:
        return [render_cell(cell) for cell in row]

    elements: list[Any] = [Align(str(clues) + " |", align="right")]
    for i in range(0, len(row), 5):
        elements.extend([render_cell(cell) for cell in row[i : i + 5]])
        elements.append("|")
    return elements


def render_blank_row(puzzle_width: int) -> list[str]:
    elements = [""]
    for _ in range(puzzle_width // 5):
        elements.extend(["--" for _ in range(5)])
        elements.append("")
    return elements


def render_column_clues(col_clues: list[LineClue]) -> list[list[Any]]:
    rows = []

    longest_col_clues = max(len(clues) for clues in col_clues)
    for row in range(longest_col_clues):
        elements = [""]

        for i, clues in enumerate(col_clues, start=1):
            n = len(clues)
            length_diff = longest_col_clues - n
            clue_index = row - length_diff
            if 0 <= clue_index < n:
                elements.append(Align(str(clues[clue_index]), align="right"))
            else:
                elements.append("")
            if i % 5 == 0:
                elements.append("")

        rows.append(elements)

    return rows


def get_grid_stats(grid: Grid) -> tuple[int, int, int]:
    complete = sum(cell != CellState.UNKNOWN for row in grid.cells for cell in row)
    total = grid.width * grid.height
    return complete, total, round(complete / total * 100, 1)
