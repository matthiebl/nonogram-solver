from nonogram.core import CellState, LineClue, LineView
from nonogram.rules import Rule


class CompleteCluesRule(Rule):
    @staticmethod
    def apply(clues: LineClue, state: LineView) -> LineView:
        black = [length for _, length in black_runs(state)]

        if list(clues) != black:
            return state

        new = LineView(state)
        for i, cell in enumerate(state):
            if cell != CellState.BLACK:
                new[i] = CellState.WHITE

        return new


def black_runs(state: LineView) -> list[tuple[int, int]]:
    """Returns a list of the sequences of black cells.

    Args:
        state (LineView): A given line state

    Returns:
        list[tuple[int, int]]: A list of (start index, length) pairs
    """
    runs = []
    pos = 0
    n = len(state)

    while pos < n:
        if state[pos] == CellState.BLACK:
            start = pos
            while pos < n and state[pos] == CellState.BLACK:
                pos += 1
            runs.append((start, pos - start))
        else:
            pos += 1

    return runs
