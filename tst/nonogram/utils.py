from nonogram.core import CellState, LineClue, LineView
from nonogram.rules import Rule
from nonogram.rules.edge_rules import EdgeRule


def assert_state(actual: LineView, expected: LineView) -> None:
    assert actual == expected, f'"{actual}" != "{expected}"'


def assert_state_at_least(actual: LineView, expected: LineView) -> None:
    assert all(b == CellState.UNKNOWN or a == b for a, b in zip(actual, expected)), (
        f'"{actual}" !>= "{expected}"'
    )


class RuleTester:
    def __init__(self, rule: Rule):
        self.rule = rule

    def assert_apply(self, clues: tuple[int, ...], initial: str, expected: str) -> None:
        assert_state(
            actual=self.rule.apply(LineClue(clues), LineView(initial)),
            expected=LineView(expected),
        )

    def assert_apply_at_least(self, clues: tuple[int, ...], initial: str, expected: str) -> None:
        """Checks that `initial` is solved at least as much as `expected`."""
        actual = self.rule.apply(LineClue(clues), LineView(initial))
        assert_state_at_least(actual, LineView(expected))


class EdgeRuleTester(RuleTester):
    def __init__(self, rule: EdgeRule):
        self.rule = rule

    def assert_apply_left_to_right(
        self, clues: tuple[int, ...], initial: str, expected: str
    ) -> None:
        assert_state(
            actual=self.rule.apply_left_to_right(LineClue(clues), LineView(initial)),
            expected=LineView(expected),
        )

    def assert_apply_left_to_right_at_least(
        self, clues: tuple[int, ...], initial: str, expected: str
    ) -> None:
        """Checks that `initial` is solved at least as much as `expected`."""
        actual = self.rule.apply_left_to_right(LineClue(clues), LineView(initial))
        assert_state_at_least(actual, LineView(expected))
