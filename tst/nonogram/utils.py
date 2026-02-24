from nonogram.core import Cell, Clues, LineState
from nonogram.rules import Rule
from nonogram.rules.edge_rules import EdgeRule


def assert_state(actual: LineState, expected: LineState) -> bool:
    assert actual == expected, f'"{actual}" != "{expected}"'
    return True


def assert_state_at_least(actual: LineState, expected: LineState) -> bool:
    assert all(b == Cell.UNKNOWN or a == b for a, b in zip(actual, expected)), (
        f'"{actual}" !>= "{expected}"'
    )
    return True


class RuleTester:
    def __init__(self, rule: Rule):
        self.rule = rule

    def assert_apply(self, clues: tuple[int, ...], initial: str, expected: str) -> None:
        assert_state(
            actual=self.rule.apply(Clues(clues), LineState(initial)),
            expected=LineState(expected),
        )

    def assert_apply_at_least(self, clues: tuple[int, ...], initial: str, expected: str) -> None:
        """Checks that `initial` is solved at least as much as `expected`."""
        actual = self.rule.apply(Clues(clues), LineState(initial))
        assert_state_at_least(actual, LineState(expected))


class EdgeRuleTester(RuleTester):
    def __init__(self, rule: EdgeRule):
        self.rule = rule

    def assert_apply_left_to_right(
        self, clues: tuple[int, ...], initial: str, expected: str
    ) -> None:
        assert_state(
            actual=self.rule.apply_left_to_right(Clues(clues), LineState(initial)),
            expected=LineState(expected),
        )

    def assert_apply_left_to_right_at_least(
        self, clues: tuple[int, ...], initial: str, expected: str
    ) -> None:
        """Checks that `initial` is solved at least as much as `expected`."""
        actual = self.rule.apply_left_to_right(Clues(clues), LineState(initial))
        assert_state_at_least(actual, LineState(expected))
