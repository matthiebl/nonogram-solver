from nonogram.core import Clues, LineState
from nonogram.rules import Rule


class LineSolver:
    def __init__(self, rules: list[Rule]):
        self.rules = rules

    def solve(self, clues: Clues, state: LineState) -> LineState:
        """Solves as much of the given state as possible with the clues.

        Args:
            clues (LineClue): List of clues valid over the state.
            state (LineView): Line state to apply the rule to.

        Returns:
            LineView: The (potentially) updated line state.
        """
        prev: LineState | None = None
        curr = LineState(state)

        while curr != prev:
            prev = curr
            for rule in self.rules:
                curr = rule.apply(clues, curr)

        return curr
