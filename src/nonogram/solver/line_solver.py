from math import comb

from nonogram.core import LineClue, LineView
from nonogram.rules import Rule
from nonogram.rules.enumeration_rules import EnumerationRule


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

        complexity = line_complexity(clues, len(curr))
        if complexity < 50_000:
            curr = EnumerationRule.apply(clues, curr)

        return curr


def line_complexity(clues: LineClue, length: int) -> float:
    k = len(clues)
    if k == 0:
        return 1
    slack = length - (sum(clues) + k - 1)
    if slack < 0:
        return float("inf")
    return comb(slack + k, k)
