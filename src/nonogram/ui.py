from __future__ import annotations

import json
import time
from pathlib import Path

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.timer import Timer
from textual.widget import Widget
from textual.widgets import Button, DirectoryTree, Input, Label, Static

from nonogram.core import Cell, Clues, Grid
from nonogram.parser import ParseError, PuzzleInput, parse_nonogram
from nonogram.solver.ui_solver import StepResult, StepwiseSolver

# ──────────────────────────────────────────────────────────────────────────────
# Grid widget
# ──────────────────────────────────────────────────────────────────────────────

CELL_CYCLE = [Cell.UNKNOWN, Cell.BOX, Cell.CROSS]


class GridWidget(Widget):
    """Renders the nonogram grid with clues; supports cursor and edit mode."""

    can_focus = True

    DEFAULT_CSS = """
    GridWidget {
        width: auto;
        height: auto;
    }
    """

    cursor: reactive[tuple[int, int]] = reactive((0, 0))
    edit_mode: reactive[bool] = reactive(False)

    def __init__(self, puzzle: PuzzleInput, solver: StepwiseSolver) -> None:
        super().__init__()
        self.puzzle = puzzle
        self.solver = solver
        self.highlighted_cells: set[tuple[int, int]] = set()

    # ── Layout helpers ──────────────────────────────────────────────────────

    def _max_row_clue_width(self) -> int:
        if not self.puzzle.row_clues:
            return 0
        return max(len(str(c)) for c in self.puzzle.row_clues)

    def _num_col_clue_rows(self) -> int:
        if not self.puzzle.col_clues:
            return 0
        return max(len(c) for c in self.puzzle.col_clues)

    def _cell_char_x(self, col: int) -> int:
        """Character x-offset of the left edge of cell at grid column `col`."""
        clue_w = self._max_row_clue_width()
        return clue_w + 3 + col * 2 + col // 5  # 3 = " | "

    def _cell_char_y(self, row: int) -> int:
        """Character y-offset of the grid row `row`."""
        col_clue_rows = self._num_col_clue_rows()
        # +1 for blank separator row after column clues
        return col_clue_rows + 1 + row + row // 5

    # ── Rendering ───────────────────────────────────────────────────────────

    def render(self) -> Text:
        grid = self.solver.grid
        row_clues = self.puzzle.row_clues
        col_clues = self.puzzle.col_clues
        width = self.puzzle.width
        height = self.puzzle.height

        clue_w = self._max_row_clue_width()
        col_clue_rows = self._num_col_clue_rows()
        cur_row, cur_col = self.cursor

        lines: list[str] = []

        # ── Column clue header ───────────────────────────────────────────
        for clue_row in range(col_clue_rows):
            parts: list[str] = [" " * (clue_w + 3)]  # indent to align with grid
            for j, clues in enumerate(col_clues):
                depth = len(clues)
                offset = clue_row - (col_clue_rows - depth)
                if 0 <= offset < depth:
                    parts.append(f"{clues[offset]:>2}")
                else:
                    parts.append("  ")
                if (j + 1) % 5 == 0:
                    parts.append(" ")
            lines.append("".join(parts))

        # Blank separator
        sep = " " * (clue_w + 3) + ("--" * min(5, width) + " ") * (width // 5) + "--" * (width % 5)
        lines.append(sep)

        # ── Grid rows ────────────────────────────────────────────────────
        for i, (clues, row_cells) in enumerate(zip(row_clues, grid.cells)):
            clue_str = str(clues)
            line_parts: list[str] = [f"{clue_str:>{clue_w}} | "]
            for j, cell in enumerate(row_cells):
                is_cursor = self.edit_mode and (i == cur_row) and (j == cur_col)
                is_highlighted = (i, j) in self.highlighted_cells
                if cell == Cell.BOX:
                    if is_cursor:
                        line_parts.append("\x1b[1m██\x1b[0m")
                    elif is_highlighted:
                        line_parts.append("\x1b[32m██\x1b[0m")
                    else:
                        line_parts.append("██")
                elif cell == Cell.CROSS:
                    if is_cursor:
                        line_parts.append("\x1b[7m░░\x1b[0m")
                    elif is_highlighted:
                        line_parts.append("\x1b[92m░░\x1b[0m")
                    else:
                        line_parts.append("░░")
                else:  # UNKNOWN
                    if is_cursor:
                        line_parts.append("\x1b[7m  \x1b[0m")
                    elif is_highlighted:
                        line_parts.append("\x1b[42m  \x1b[0m")
                    else:
                        line_parts.append("  ")
                if (j + 1) % 5 == 0 and j + 1 < width:
                    line_parts.append("|")
            lines.append("".join(line_parts))
            if (i + 1) % 5 == 0 and i + 1 < height:
                lines.append(sep)

        text = Text.from_ansi("\n".join(lines))
        return text

    # ── Mouse events ────────────────────────────────────────────────────────

    def on_click(self, event: Widget.Click) -> None:
        if not self.edit_mode:
            return
        col_clue_rows = self._num_col_clue_rows()
        clue_w = self._max_row_clue_width()

        x, y = event.x, event.y
        # y: subtract col clue area and separator row
        grid_y = y - col_clue_rows - 1
        if grid_y < 0:
            return

        # Account for separator rows every 5
        row = grid_y - grid_y // 6  # every 6th "row slot" is a separator
        if row >= self.puzzle.height or row < 0:
            return

        # x: subtract clue area ("clue_w + 3" chars)
        grid_x = x - (clue_w + 3)
        if grid_x < 0:
            return

        # Account for "|" separator every 10 chars (5 cols × 2 chars + 1 sep)
        col = (grid_x - grid_x // 11) // 2
        if col >= self.puzzle.width or col < 0:
            return

        self.cursor = (row, col)
        self._cycle_cell(row, col)

    # ── Keyboard events ─────────────────────────────────────────────────────

    def on_key(self, event: Widget.Key) -> None:
        if not self.edit_mode:
            return
        row, col = self.cursor
        h, w = self.puzzle.height, self.puzzle.width

        if event.key == "up":
            self.cursor = (max(0, row - 1), col)
            event.stop()
        elif event.key == "down":
            self.cursor = (min(h - 1, row + 1), col)
            event.stop()
        elif event.key == "left":
            self.cursor = (row, max(0, col - 1))
            event.stop()
        elif event.key == "right":
            self.cursor = (row, min(w - 1, col + 1))
            event.stop()
        elif event.key in ("space", "enter"):
            self._cycle_cell(row, col)
            event.stop()

    def _cycle_cell(self, row: int, col: int) -> None:
        current = self.solver.grid.cells[row][col]
        idx = CELL_CYCLE.index(current)
        next_cell = CELL_CYCLE[(idx + 1) % len(CELL_CYCLE)]
        self.solver.set_cell(row, col, next_cell)
        self.refresh()
        if isinstance(self.screen, SolverScreen):
            self.screen.refresh_status()

    def watch_cursor(self, _: tuple[int, int]) -> None:
        self.refresh()

    def watch_edit_mode(self, _: bool) -> None:
        self.refresh()


# ──────────────────────────────────────────────────────────────────────────────
# Load screen
# ──────────────────────────────────────────────────────────────────────────────


class JsonLoadPanel(Container):
    DEFAULT_CSS = """
    JsonLoadPanel {
        height: auto;
        border: solid $accent;
        padding: 1;
    }
    JsonLoadPanel Label { margin-bottom: 1; }
    JsonLoadPanel DirectoryTree { height: 20; }
    JsonLoadPanel #load-error { color: $error; }
    """

    def compose(self) -> ComposeResult:
        yield Label("Select a .json puzzle file:")
        yield DirectoryTree(str(Path.cwd()), id="file-tree")
        yield Label("", id="load-error")

    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        path = str(event.path)
        if not path.endswith(".json"):
            self.query_one("#load-error", Label).update("Please select a .json file.")
            return
        try:
            puzzle = parse_nonogram(path)
        except (ParseError, Exception) as exc:
            self.query_one("#load-error", Label).update(f"Error: {exc}")
            return
        self.app.push_screen(SolverScreen(puzzle))


class LoadScreen(Screen):
    DEFAULT_CSS = """
    LoadScreen {
        align: center middle;
    }
    LoadScreen #load-container {
        width: 70;
        height: auto;
        padding: 2;
        border: double $accent;
    }
    LoadScreen #load-container Label.title {
        text-align: center;
        text-style: bold;
        margin-bottom: 2;
        width: 100%;
    }
    LoadScreen #btn-row {
        height: auto;
        margin-bottom: 2;
    }
    LoadScreen Button {
        width: 1fr;
        margin: 0 1;
    }
    LoadScreen #json-panel { display: none; }
    LoadScreen #json-panel.visible { display: block; }
    """

    def compose(self) -> ComposeResult:
        with Container(id="load-container"):
            yield Label("Nonogram Solver", classes="title")
            with Horizontal(id="btn-row"):
                yield Button("Load JSON file", id="btn-json", variant="primary")
                yield Button("Enter manually", id="btn-manual", variant="default")
            yield JsonLoadPanel(id="json-panel")

    @on(Button.Pressed, "#btn-json")
    def show_json_panel(self) -> None:
        panel = self.query_one("#json-panel")
        panel.toggle_class("visible")

    @on(Button.Pressed, "#btn-manual")
    def go_manual(self) -> None:
        self.app.push_screen(ManualSizeScreen())


# ──────────────────────────────────────────────────────────────────────────────
# Manual entry screens
# ──────────────────────────────────────────────────────────────────────────────


class ManualSizeScreen(Screen):
    DEFAULT_CSS = """
    ManualSizeScreen {
        align: center middle;
    }
    ManualSizeScreen #container {
        width: 50;
        height: auto;
        padding: 2;
        border: double $accent;
    }
    ManualSizeScreen Label.title {
        text-align: center;
        text-style: bold;
        margin-bottom: 2;
        width: 100%;
    }
    ManualSizeScreen .field-row {
        height: auto;
        margin-bottom: 1;
    }
    ManualSizeScreen .field-row Label {
        width: 10;
        padding-top: 1;
    }
    ManualSizeScreen .field-row Input {
        width: 1fr;
    }
    ManualSizeScreen #error { color: $error; margin-top: 1; }
    ManualSizeScreen #btn-row { margin-top: 2; height: auto; }
    ManualSizeScreen #btn-row Button { width: 1fr; margin: 0 1; }
    """

    def compose(self) -> ComposeResult:
        with Container(id="container"):
            yield Label("Create Puzzle", classes="title")
            with Horizontal(classes="field-row"):
                yield Label("Width:")
                yield Input(placeholder="e.g. 5", id="width-input")
            with Horizontal(classes="field-row"):
                yield Label("Height:")
                yield Input(placeholder="e.g. 5", id="height-input")
            yield Label("", id="error")
            with Horizontal(id="btn-row"):
                yield Button("Back", id="btn-back", variant="default")
                yield Button("Next", id="btn-next", variant="primary")

    @on(Button.Pressed, "#btn-back")
    def go_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-next")
    def go_next(self) -> None:
        error = self.query_one("#error", Label)
        try:
            w = int(self.query_one("#width-input", Input).value)
            h = int(self.query_one("#height-input", Input).value)
            if w < 1 or h < 1:
                raise ValueError("Width and height must be positive integers.")
        except ValueError as exc:
            error.update(str(exc))
            return
        error.update("")
        self.app.push_screen(ManualCluesScreen(w, h))


def _parse_clue_line(text: str) -> list[int]:
    """Parse a space-separated string of ints, e.g. '1 2 3'. Empty string → [0]."""
    text = text.strip()
    if not text:
        return [0]
    return [int(x) for x in text.split()]


class ManualCluesScreen(Screen):
    DEFAULT_CSS = """
    ManualCluesScreen {
        align: center middle;
    }
    ManualCluesScreen #outer {
        width: 70;
        height: 90%;
        border: double $accent;
    }
    ManualCluesScreen Label.title {
        text-align: center;
        text-style: bold;
        margin: 1 0;
        width: 100%;
    }
    ManualCluesScreen Label.section {
        text-style: bold;
        margin-top: 1;
    }
    ManualCluesScreen .clue-row {
        height: auto;
        margin-bottom: 0;
    }
    ManualCluesScreen .clue-row Label {
        width: 12;
        padding-top: 1;
    }
    ManualCluesScreen .clue-row Input {
        width: 1fr;
    }
    ManualCluesScreen #error { color: $error; margin: 1 2; }
    ManualCluesScreen #btn-row { margin: 1 2; height: auto; }
    ManualCluesScreen #btn-row Button { width: 1fr; margin: 0 1; }
    """

    def __init__(self, width: int, height: int) -> None:
        super().__init__()
        self._width = width
        self._height = height

    def compose(self) -> ComposeResult:
        with Container(id="outer"):
            yield Label(f"Enter Clues ({self._width}×{self._height})", classes="title")
            with ScrollableContainer():
                yield Label("Row clues (space-separated, left→right):", classes="section")
                for i in range(self._height):
                    with Horizontal(classes="clue-row"):
                        yield Label(f"Row {i + 1}:")
                        yield Input(placeholder="e.g. 1 2", id=f"row-{i}")
                yield Label("Column clues (space-separated, top→bottom):", classes="section")
                for j in range(self._width):
                    with Horizontal(classes="clue-row"):
                        yield Label(f"Col {j + 1}:")
                        yield Input(placeholder="e.g. 3", id=f"col-{j}")
            yield Label("", id="error")
            with Horizontal(id="btn-row"):
                yield Button("Back", id="btn-back", variant="default")
                yield Button("Create Puzzle", id="btn-create", variant="primary")

    @on(Button.Pressed, "#btn-back")
    def go_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-create")
    def create_puzzle(self) -> None:
        error = self.query_one("#error", Label)
        try:
            row_clues = [
                Clues(_parse_clue_line(self.query_one(f"#row-{i}", Input).value))
                for i in range(self._height)
            ]
            col_clues = [
                Clues(_parse_clue_line(self.query_one(f"#col-{j}", Input).value))
                for j in range(self._width)
            ]
        except ValueError as exc:
            error.update(f"Invalid clue: {exc}")
            return

        row_sum = sum(sum(c) for c in row_clues)
        col_sum = sum(sum(c) for c in col_clues)
        if row_sum != col_sum:
            error.update(f"Row clue total ({row_sum}) ≠ column clue total ({col_sum}).")
            return

        puzzle = PuzzleInput(
            meta={},
            width=self._width,
            height=self._height,
            row_clues=row_clues,
            col_clues=col_clues,
            grid=Grid(self._width, self._height),
        )
        error.update("")
        self.app.push_screen(SolverScreen(puzzle))


# ──────────────────────────────────────────────────────────────────────────────
# Save screen
# ──────────────────────────────────────────────────────────────────────────────


def _puzzle_to_dict(puzzle: PuzzleInput, grid: Grid) -> dict:
    """Serialize puzzle + current grid state to the JSON format."""
    grid_data = ["".join(str(cell) for cell in row) for row in grid.cells]
    data: dict = {
        "version": "1",
        "meta": puzzle.meta,
        "width": puzzle.width,
        "height": puzzle.height,
        "rows": [list(clues) for clues in puzzle.row_clues],
        "cols": [list(clues) for clues in puzzle.col_clues],
        "grid": grid_data,
    }
    return data


class SaveScreen(ModalScreen[str | None]):
    """Modal dialog for saving the puzzle to a JSON file."""

    DEFAULT_CSS = """
    SaveScreen {
        align: center middle;
    }
    SaveScreen #save-container {
        width: 70;
        height: 35;
        padding: 1 2;
        border: double $accent;
        background: $surface;
    }
    SaveScreen Label.title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        width: 100%;
    }
    SaveScreen #dir-tree {
        height: 1fr;
        margin-bottom: 1;
    }
    SaveScreen #selected-dir {
        margin-bottom: 1;
    }
    SaveScreen .field-row {
        height: auto;
        margin-bottom: 1;
    }
    SaveScreen .field-row Label {
        width: 12;
        padding-top: 1;
    }
    SaveScreen .field-row Input {
        width: 1fr;
    }
    SaveScreen #save-error { color: $error; margin-bottom: 1; }
    SaveScreen #save-btn-row { height: auto; }
    SaveScreen #save-btn-row Button { width: 1fr; margin: 0 1; }
    """

    def __init__(self, puzzle: PuzzleInput, grid: Grid) -> None:
        super().__init__()
        self._puzzle = puzzle
        self._grid = grid
        self._selected_dir: Path = Path.cwd()

    def compose(self) -> ComposeResult:
        default_name = self._puzzle.meta.get("title", "puzzle").lower().replace(" ", "_") + ".json"
        with Container(id="save-container"):
            yield Label("Save Puzzle", classes="title")
            yield Label(f"Folder: {self._selected_dir}", id="selected-dir")
            yield DirectoryTree(str(self._selected_dir), id="dir-tree")
            with Horizontal(classes="field-row"):
                yield Label("Filename:")
                yield Input(value=default_name, id="filename-input")
            yield Label("", id="save-error")
            with Horizontal(id="save-btn-row"):
                yield Button("Cancel", id="btn-cancel", variant="default")
                yield Button("Save", id="btn-save", variant="primary")

    @on(DirectoryTree.DirectorySelected)
    def on_dir_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        self._selected_dir = event.path
        self.query_one("#selected-dir", Label).update(f"Folder: {self._selected_dir}")

    @on(Button.Pressed, "#btn-cancel")
    def cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-save")
    def save(self) -> None:
        error = self.query_one("#save-error", Label)
        filename = self.query_one("#filename-input", Input).value.strip()
        if not filename:
            error.update("Please enter a filename.")
            return
        if not filename.endswith(".json"):
            filename += ".json"

        save_path = self._selected_dir / filename
        try:
            data = _puzzle_to_dict(self._puzzle, self._grid)
            save_path.write_text(json.dumps(data, indent=2) + "\n")
        except Exception as exc:
            error.update(f"Error: {exc}")
            return

        self.dismiss(str(save_path))


# ──────────────────────────────────────────────────────────────────────────────
# Solver screen
# ──────────────────────────────────────────────────────────────────────────────


class SolverScreen(Screen):
    BINDINGS = [
        Binding("s", "step", "Step", show=True),
        Binding("u", "undo", "Undo", show=True),
        Binding("r", "run", "Run", show=True),
        Binding("escape", "stop", "Stop", show=True),
        Binding("e", "toggle_edit", "Edit", show=True),
        Binding("n", "toggle_enum", "Enum", show=True),
        Binding("ctrl+s", "save", "Save", show=True),
        Binding("x", "reset", "Reset", show=True),
        Binding("q", "quit_app", "Quit", show=True),
    ]

    DEFAULT_CSS = """
    SolverScreen {
        layout: vertical;
    }
    SolverScreen #header {
        height: 3;
        layout: horizontal;
    }
    SolverScreen #header #title {
        width: 1fr;
        content-align: left middle;
        padding: 0 2;
        border: solid $accent;
    }
    SolverScreen #header #progress {
        width: 30;
        content-align: right middle;
        padding: 0 2;
        border: solid $accent;
    }
    SolverScreen #grid-scroll {
        height: 1fr;
        overflow: auto;
        align: center middle;
    }
    SolverScreen #footer {
        height: auto;
        border-top: solid $accent;
        padding: 1;
    }
    SolverScreen #btn-bar {
        height: auto;
        margin-bottom: 1;
    }
    SolverScreen #btn-bar Button {
        margin: 0 1;
        min-width: 10;
    }
    SolverScreen #status {
        height: auto;
        padding: 0 1;
    }
    """

    def __init__(self, puzzle: PuzzleInput) -> None:
        super().__init__()
        self.puzzle = puzzle
        self.solver = StepwiseSolver(puzzle)
        self._run_timer: Timer | None = None
        self._start_time = time.time()
        self._is_editing = False

    def compose(self) -> ComposeResult:
        title = self.puzzle.meta.get("title", "Nonogram")
        with Horizontal(id="header"):
            yield Static(f"  {title}", id="title")
            yield Static("0% (0/0)", id="progress")
        with ScrollableContainer(id="grid-scroll"):
            yield GridWidget(self.puzzle, self.solver)
        with Vertical(id="footer"):
            with Horizontal(id="btn-bar"):
                yield Button("Step (s)", id="btn-step", variant="primary")
                yield Button("Undo (u)", id="btn-undo", variant="default")
                yield Button("Run (r)", id="btn-run", variant="success")
                yield Button("Stop (esc)", id="btn-stop", variant="warning")
                yield Button("Edit (e)", id="btn-edit", variant="default")
                yield Button("Enum (n)", id="btn-enum", variant="default")
                yield Button("Save (^s)", id="btn-save", variant="default")
                yield Button("Reset (x)", id="btn-reset", variant="warning")
                yield Button("Quit (q)", id="btn-quit", variant="error")
            yield Static("Ready. Press 's' to step or 'r' to run.", id="status")

    # ── Button handlers ─────────────────────────────────────────────────────

    @on(Button.Pressed, "#btn-step")
    def btn_step(self) -> None:
        self.action_step()

    @on(Button.Pressed, "#btn-undo")
    def btn_undo(self) -> None:
        self.action_undo()

    @on(Button.Pressed, "#btn-run")
    def btn_run(self) -> None:
        self.action_run()

    @on(Button.Pressed, "#btn-stop")
    def btn_stop(self) -> None:
        self.action_stop()

    @on(Button.Pressed, "#btn-edit")
    def btn_edit(self) -> None:
        self.action_toggle_edit()

    @on(Button.Pressed, "#btn-enum")
    def btn_enum(self) -> None:
        self.action_toggle_enum()

    @on(Button.Pressed, "#btn-save")
    def btn_save(self) -> None:
        self.action_save()

    @on(Button.Pressed, "#btn-reset")
    def btn_reset(self) -> None:
        self.action_reset()

    @on(Button.Pressed, "#btn-quit")
    def btn_quit(self) -> None:
        self.action_quit_app()

    # ── Actions ─────────────────────────────────────────────────────────────

    def action_step(self) -> None:
        self.action_stop()
        # Advance until a line actually changes, a repopulation occurs, or we finish/get stuck
        result = None
        while True:
            result = self.solver.step()
            if result is None or result.changed or result.kind == "repopulate" or result.is_done:
                break
        self._after_step(result)

    def action_undo(self) -> None:
        self.action_stop()
        if self.solver.undo():
            self.query_one(GridWidget).highlighted_cells = set()
            self._refresh_grid()
            self.refresh_status("Undone.")
        else:
            self.refresh_status("Nothing to undo.")

    def action_run(self) -> None:
        if self._run_timer is not None:
            return
        self._run_timer = self.set_interval(0.03, self._run_tick)
        self.refresh_status("Running...")

    def action_stop(self) -> None:
        if self._run_timer is not None:
            self._run_timer.stop()
            self._run_timer = None

    def action_reset(self) -> None:
        self.action_stop()
        self.solver.reset()
        self._start_time = time.time()
        grid_widget = self.query_one(GridWidget)
        grid_widget.highlighted_cells = set()
        grid_widget.edit_mode = False
        grid_widget.cursor = (0, 0)
        self._is_editing = False
        self.query_one("#btn-edit", Button).variant = "default"
        self._refresh_grid()
        self.refresh_status("Puzzle reset.")

    def action_toggle_edit(self) -> None:
        self.action_stop()
        self._is_editing = not self._is_editing
        grid_widget = self.query_one(GridWidget)
        grid_widget.edit_mode = self._is_editing
        btn = self.query_one("#btn-edit", Button)
        if self._is_editing:
            btn.variant = "warning"
            self.refresh_status("Edit mode — use arrows + space or click to toggle cells.")
            grid_widget.focus()
        else:
            btn.variant = "default"
            self.refresh_status("Edit mode off.")

    def action_save(self) -> None:
        self.action_stop()

        def on_save_result(result: str | None) -> None:
            if result:
                self.refresh_status(f"Saved to {result}")
                self.notify(f"Saved: {result}")
            else:
                self.refresh_status("Save cancelled.")

        self.app.push_screen(SaveScreen(self.puzzle, self.solver.grid), on_save_result)

    def action_toggle_enum(self) -> None:
        enabled = self.solver.toggle_enumeration()
        btn = self.query_one("#btn-enum", Button)
        if enabled:
            btn.variant = "warning"
            self.refresh_status("Enumeration rule enabled.")
        else:
            btn.variant = "default"
            self.refresh_status("Enumeration rule disabled.")

    def action_quit_app(self) -> None:
        self.app.exit()

    # ── Timer tick ───────────────────────────────────────────────────────────

    def _run_tick(self) -> None:
        result = self.solver.step()
        self._after_step(result)
        if result is None or result.is_done or result.is_stuck:
            self.action_stop()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _after_step(self, result: StepResult | None) -> None:
        grid_widget = self.query_one(GridWidget)
        grid_widget.highlighted_cells = (
            result.updated_cells if result and result.updated_cells else set()
        )
        self._refresh_grid()
        if result is None:
            if self.solver.is_done:
                self.refresh_status("Puzzle solved!")
            else:
                self.refresh_status("Stuck — no further progress possible.")
            return

        grid = self.solver.grid
        complete = sum(cell != Cell.UNKNOWN for row in grid.cells for cell in row)
        total = self.puzzle.width * self.puzzle.height

        if result.error:
            self.refresh_status(result.error)
            self.notify(result.error, severity="error")
            return
        elif result.kind == "repopulate":
            msg = f"Queue exhausted, restarting pass... ({complete}/{total} complete)"
        elif result.is_done:
            elapsed = time.time() - self._start_time
            msg = f"Puzzle solved! {complete}/{total} in {elapsed:.1f}s"
        elif result.changed:
            msg = f"Updated {result.kind} {result.index + 1} — {complete}/{total} cells complete"
        else:
            msg = f"No change in {result.kind} {result.index + 1} — {complete}/{total}"

        self.refresh_status(msg)
        self._update_progress(complete, total)

    def _refresh_grid(self) -> None:
        self.query_one(GridWidget).refresh()

    def _update_progress(self, complete: int, total: int) -> None:
        pct = round(complete / total * 100, 1) if total else 0
        elapsed = time.time() - self._start_time
        mins, secs = divmod(int(elapsed), 60)
        self.query_one("#progress", Static).update(
            f"{mins:02d}:{secs:02d} — {pct}% ({complete}/{total})"
        )

    def refresh_status(self, msg: str = "") -> None:
        if msg:
            self.query_one("#status", Static).update(msg)
        complete = sum(cell != Cell.UNKNOWN for row in self.solver.grid.cells for cell in row)
        total = self.puzzle.width * self.puzzle.height
        self._update_progress(complete, total)


# ──────────────────────────────────────────────────────────────────────────────
# App
# ──────────────────────────────────────────────────────────────────────────────


class NonogramApp(App):
    def __init__(self, input_path: str | None = None) -> None:
        super().__init__()
        self._input_path = input_path

    def on_mount(self) -> None:
        if self._input_path:
            try:
                puzzle = parse_nonogram(self._input_path)
                self.push_screen(SolverScreen(puzzle))
            except (ParseError, Exception) as exc:
                self.push_screen(LoadScreen())
                self.notify(f"Failed to load {self._input_path}: {exc}", severity="error")
        else:
            self.push_screen(LoadScreen())
