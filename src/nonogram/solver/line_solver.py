from collections import defaultdict
from math import comb

from nonogram.core import LineClue, LineView
from nonogram.rules import Rule


class LineSolver:
    def __init__(self, rules: list[Rule]):
        self.rules = rules

        self.complexity_cache = defaultdict(lambda: 2_500_000)
        self.retry_last_line = False

    def solve(self, clues: LineClue, state: LineView) -> LineView:
        """Solves as much of the given state as possible with the clues.

        Args:
            clues (LineClue): List of clues valid over the state.
            state (LineView): Line state to apply the rule to.

        Returns:
            LineView: The (potentially) updated line state.
        """
        self.retry_last_line = False

        prev: LineView | None = None
        curr = LineView(state)

        complexity = line_complexity(clues, len(state))
        is_complex = False
        if complexity > self.complexity_cache[(clues, len(state))]:
            is_complex = True
            self.complexity_cache[(clues, len(state))] *= 1.1

        while curr != prev:
            prev = curr
            for rule in self.rules:
                if is_complex and rule.cost == "HIGH":
                    self.retry_last_line = True
                    continue
                curr = rule.apply(clues, curr)

        return curr


def line_complexity(clues: LineClue, length: int) -> float:
    k = len(clues)
    if k == 0:
        return 1
    slack = length - (sum(clues) + k - 1)
    if slack < 0:
        return float("inf")
    return comb(slack + k, k)
