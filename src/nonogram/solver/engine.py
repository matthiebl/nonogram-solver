from collections import deque

from nonogram.core import Grid, LineClue
from nonogram.solver.line_solver import LineSolver


class PropagationEngine:
    def __init__(self, line_solver: LineSolver) -> None:
        self.line_solver = line_solver

    def propagate(self, grid: Grid, row_clues: list[LineClue], col_clues: list[LineClue]) -> bool:
        """Propagates a grid as far as possible using the engine's line solver.

        Args:
            grid (Grid): The current grid
            row_clues (list[LineClue]): The clues of each row
            col_clues (list[LineClue]): The clues of each column

        Returns:
            bool: Whether or not the grid was successfully updated.
        """
        queue = deque(
            [("row", i) for i in range(grid.height)] + [("col", j) for j in range(grid.width)]
        )

        changed = False

        while queue:
            kind, index = queue.popleft()

            clues = row_clues[index] if kind == "row" else col_clues[index]
            line = grid.row(index) if kind == "row" else grid.col(index)

            new_line = self.line_solver.solve(clues, line)
            if (
                grid.apply_row(index, new_line)
                if kind == "row"
                else grid.apply_col(index, new_line)
            ):
                changed = True
                updated_indices = [
                    i for i, (old, new) in enumerate(zip(line, new_line)) if old != new
                ]
                queue.extend([("col" if kind == "row" else "row", i) for i in updated_indices])

        return changed
