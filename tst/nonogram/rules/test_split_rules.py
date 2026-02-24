import pytest

from nonogram.core import Clues, LineState
from nonogram.rules.split_rules import CompleteEdgeSplitRule, consume_complete_prefix


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
        segments = rule.split(Clues(clues), LineState(state))
        assert segments == tuple((Clues(clue), LineState(state)) for clue, state in expected)

        state_segments = [state for _, state in segments]
        assert rule.merge(state_segments) == LineState(state)


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
        assert consume_complete_prefix(Clues(clues), LineState(state)) == (
            Clues(a_clue),
            LineState(a_state),
            Clues(b_clue),
            LineState(b_state),
        )
