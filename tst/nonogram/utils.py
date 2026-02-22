from nonogram.core import CellState, LineClue, LineView
from nonogram.rules import Rule
from nonogram.rules.edge_rules import EdgeRule


class RuleTester:
    def __init__(self, rule: Rule):
        self.rule = rule

    def assert_apply(self, clues: tuple[int, ...], initial: str, expected: str) -> None:
        assert self.rule.apply(LineClue(clues), LineView(initial)) == LineView(expected)

    def assert_apply_at_least(self, clues: tuple[int, ...], initial: str, expected: str) -> None:
        """Checks that `initial` is solved at least as much as `expected`."""
        actual = self.rule.apply(LineClue(clues), LineView(initial))
        assert all(b == CellState.UNKNOWN or a == b for a, b in zip(actual, LineView(expected)))


class EdgeRuleTester(RuleTester):
    def __init__(self, rule: EdgeRule):
        self.rule = rule

    def assert_apply_left_to_right(
        self, clues: tuple[int, ...], initial: str, expected: str
    ) -> None:
        assert self.rule.apply_left_to_right(LineClue(clues), LineView(initial)) == LineView(
            expected
        )

    def assert_apply_left_to_right_at_least(
        self, clues: tuple[int, ...], initial: str, expected: str
    ) -> None:
        """Checks that `initial` is solved at least as much as `expected`."""
        actual = self.rule.apply_left_to_right(LineClue(clues), LineView(initial))
        assert all(b == CellState.UNKNOWN or a == b for a, b in zip(actual, LineView(expected)))
