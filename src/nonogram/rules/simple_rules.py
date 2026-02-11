from nonogram.core import CellState, LineClue, LineView
from nonogram.rules import Rule
from nonogram.rules.utils import black_runs


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
