from nonogram.core import Grid, LineClue


class NonogramPrinter:
    def __init__(self, grid: Grid, row_clues: list[LineClue], col_clues: list[LineClue]) -> None:
        self.grid = grid
        self.row_clues = row_clues
        self.col_clues = col_clues

    def __str__(self) -> str:
        output = ""

        for i in range(self.grid.height):
            output += " ".join(map(str, self.grid.row(i))) + "\n"

        return output
