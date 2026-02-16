from math import comb

from nonogram.core import LineClue, LineView
from nonogram.rules import Rule
from nonogram.rules.enumeration_rules import EnumerationRule
from nonogram.rules.split_rules import CompleteEdgeSplitRule


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
        solved_segments = []
        segments = CompleteEdgeSplitRule.apply(clues, state)

        for segment_clues, segment in segments:
            prev: LineView | None = None
            curr = LineView(segment)

            while curr != prev:
                prev = curr
                for rule in self.rules:
                    curr = rule.apply(segment_clues, curr)

            complexity = line_complexity(segment_clues, len(segment))
            if complexity < 50_000:
                curr = EnumerationRule.apply(segment_clues, curr)

            solved_segments.extend(curr.state())

        return LineView(solved_segments)


def line_complexity(clues: LineClue, length: int) -> float:
    k = len(clues)
    if k == 0:
        return 1
    slack = length - (sum(clues) + k - 1)
    if slack < 0:
        return float("inf")
    return comb(slack + k, k)
