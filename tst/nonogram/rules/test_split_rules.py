import pytest

from nonogram.core import LineClue, LineView
from nonogram.rules.split_rules import CompleteEdgeSplitRule, consume_complete_prefix


class TestCompleteEdgeSplitRule:
    @pytest.mark.parametrize(
        "clues, line, outcome",
        [
            ([1], "     ", [([1], "     ")]),
            ([1], "#.   ", [([1], "#."), ([], "   ")]),
            ([1], "   .#", [([], "   "), ([1], ".#")]),
            ([1, 1], "#. .#", [([1], "#."), ([], " "), ([1], ".#")]),
        ],
    )
    def test_left_to_right(self, clues, line, outcome):
        assert CompleteEdgeSplitRule.apply(LineClue(clues), LineView(line)) == tuple(
            (LineClue(clue), LineView(state)) for clue, state in outcome
        )


class TestConsumeHelper:
    @pytest.mark.parametrize(
        "clues, line, outcome",
        [
            ([], "        ", ([], "", [], "        ")),
            ([1, 2, 3], "              ", ([], "", [1, 2, 3], "              ")),
            ([1], "#.  ", ([1], "#.", [], "  ")),
            ([1], "#.", ([1], "#.", [], "")),
            ([1], "#", ([1], "#", [], "")),
            ([1], ". ", ([], ".", [1], " ")),
        ],
    )
    def test_left_to_right(self, clues, line, outcome):
        a_clue, a_state, b_clue, b_state = outcome
        assert consume_complete_prefix(LineClue(clues), LineView(line)) == (
            LineClue(a_clue),
            LineView(a_state),
            LineClue(b_clue),
            LineView(b_state),
        )
