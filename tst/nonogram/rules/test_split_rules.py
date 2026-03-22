import pytest

from nonogram.core import Clues, LineState
from nonogram.rules.split_rules import (
    CompleteEdgeSplitRule,
    CrossBoundedSplitRule,
    consume_complete_prefix,
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
        segments = rule.split(Clues(clues), LineState(state))
        assert segments == tuple((Clues(clue), LineState(state)) for clue, state in expected)

        state_segments = [state for _, state in segments]
        assert rule.merge(state_segments) == LineState(state)


class TestCrossBoundedSplitRule:
    # Helper: build expected segments from (clue_tuple, state_str) pairs
    @staticmethod
    def segments(*pairs):
        return tuple((Clues(c), LineState(s)) for c, s in pairs)

    @pytest.mark.parametrize(
        "clues, state, expected",
        [
            ((2, 3), "         ", (((2, 3), "         "),)),
            ((2,), ".    ", (((2,), ".    "),)),
            ((1, 2), ".     ", (((1, 2), ".     "),)),
            ((3,), "..     ", (((3,), "..     "),)),
            ((2,), "##.", (((2,), "##."),)),
            ((1, 1), "#.#", (((1, 1), "#.#"),)),
            ((2, 3), "    .    ", (((2,), "    ."), ((3,), "    "))),
            ((2, 3), "         .    ", (((2, 3), "         .    "),)),
            ((1, 1, 3), "  .     ", (((1,), "  ."), ((1, 3), "     "))),
            ((2,), "  ..", (((2,), "  ."), ((), "."))),
            ((2,), "  .", (((2,), "  ."), ((), ""))),
            ((1, 1), "  . . ", (((1, 1), "  . . "),)),
            # ((1, 1, 1), " . . .", (((1, 1, 1), " . . ."),)),
            (
                (2, 1),
                "                 #             .... #.. ",
                (((2, 1), "                 #             .... #.. "),),
            ),
        ],
    )
    def test_split(self, clues, state, expected):
        rule = CrossBoundedSplitRule()
        segments = rule.split(Clues(clues), LineState(state))
        assert segments == self.segments(*expected)

    @pytest.mark.parametrize(
        "clues, state",
        [
            ((2, 3), "    .    "),
            ((1, 1, 3), "  .     "),
            ((2,), "  ."),
            ((2,), "  .."),
            ((1, 1), "  . . "),
            ((1, 1, 1), " . . ."),
        ],
    )
    def test_merge_roundtrip(self, clues, state):
        rule = CrossBoundedSplitRule()
        segments = rule.split(Clues(clues), LineState(state))
        state_segments = tuple(s for _, s in segments)
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
