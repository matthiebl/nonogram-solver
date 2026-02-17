from nonogram.core import LineClue, LineView
from nonogram.rules import Rule


class LineSolver:
    def __init__(self, rules: list[Rule]):
        self.rules = rules

    def solve(self, clues: LineClue, state: LineView) -> LineView:
        """Solves as much of the given state as possible with the clues.

        Args:
            clues (LineClue): List of clues valid over the state.
            state (LineView): Line state to apply the rule to.

        Returns:
            LineView: The (potentially) updated line state.
        """
        prev: LineView | None = None
        curr = LineView(state)

        while curr != prev:
            prev = curr
            for rule in self.rules:
                curr = rule.apply(clues, curr)

        return curr
