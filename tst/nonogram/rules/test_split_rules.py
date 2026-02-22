import pytest

from nonogram.core import LineClue, LineView
from nonogram.rules.split_rules import (
    CompleteEdgeSplitRule,
    consume_complete_prefix,
    forced_run_assignment,
)


class TestCompleteEdgeSplitRule:
    @pytest.mark.parametrize(
        "clues, state, expected",
        [
            ((1,), "     ", (((1,), "     "),)),
            ((1,), "#.   ", (((1,), "#."), ((), "   "))),
            ((1,), "   .#", (((), "   "), ((1,), ".#"))),
            ((1, 1), "#. .#", (((1,), "#."), ((), " "), ((1,), ".#"))),
            ((1, 1), "#  .#", (((1,), "#  "), ((1,), ".#"))),
        ],
    )
    def test_left_to_right(self, clues, state, expected):
        rule = CompleteEdgeSplitRule()
        segments = rule.split(LineClue(clues), LineView(state))
        assert segments == tuple((LineClue(clue), LineView(state)) for clue, state in expected)

        state_segments = [state for _, state in segments]
        assert rule.merge(state_segments) == LineView(state)


class TestConsumeHelper:
    @pytest.mark.parametrize(
        "clues, state, expected",
        [
            ((), "        ", ((), "", (), "        ")),
            ((1, 2, 3), "              ", ((), "", (1, 2, 3), "              ")),
            ((1,), "#.  ", ((1,), "#.", (), "  ")),
            ((1,), "#.", ((1,), "#.", (), "")),
            ((1,), "#", ((), "", (1,), "#")),
            ((1,), "# ", ((), "", (1,), "# ")),
            ((1,), ". ", ((), ".", (1,), " ")),
            ((1,), ".#.   ", ((1,), ".#.", (), "   ")),
            ((1,), ".#   ", ((), ".", (1,), "#   ")),
            ((1, 2), ".#..#   ", ((1,), ".#..", (2,), "#   ")),
            ((1, 2), ".#..##  ", ((1,), ".#..", (2,), "##  ")),
            ((1, 2), ".#..##. ", ((1, 2), ".#..##.", (), " ")),
        ],
    )
    def test_left_to_right(self, clues, state, expected):
        a_clue, a_state, b_clue, b_state = expected
        assert consume_complete_prefix(LineClue(clues), LineView(state)) == (
            LineClue(a_clue),
            LineView(a_state),
            LineClue(b_clue),
            LineView(b_state),
        )


class TestForcedRunAssignment:
    @pytest.mark.parametrize(
        "clues, state, expected",
        [
            ((2, 2, 2, 2, 5), "   .#  .#  .# ..##.   .#####..", {(23, 5): 4}),
        ],
    )
    def test_basic_usage(self, clues, state, expected):
        assert forced_run_assignment(clues, state) == expected
