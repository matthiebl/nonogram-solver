import pytest

from nonogram.core import LineClue, LineView
from nonogram.rules.edge_rules import GlueEdgeRule, MercuryEdgeRule


class TestGlueEdgeRule:
    @pytest.mark.parametrize(
        "clues, line, outcome",
        [
            ([2], "#    ", "##..."),
            ([2], ".#    ", ".##..."),
            ([2, 1], ".#    ", ".##.  "),
            ([2, 3, 1], ".# . #     ", ".##. ##    "),
            (
                [7, 9, 2],
                "       .#######  ..                               ",
                "       .#######  ..                               ",
            ),
        ],
    )
    def test_left_to_right(self, clues, line, outcome):
        assert GlueEdgeRule.apply_left_to_right(LineClue(clues), LineView(line)) == LineView(
            outcome
        )

    @pytest.mark.parametrize(
        "clues, line, outcome",
        [
            ([2], "#    ", "##..."),
            ([2], ".#    ", ".##..."),
            ([2, 1], ".#    ", ".##.  "),
            ([2, 3, 1], ".# . #     ", ".##. ##    "),
        ],
    )
    def test_apply(self, clues, line, outcome):
        assert GlueEdgeRule.apply(LineClue(clues), LineView(line)) == LineView(outcome)


class TestMercuryEdgeRule:
    @pytest.mark.parametrize(
        "clues, line, outcome",
        [
            ([1], " #    ", ".#    "),
            ([1], " #.   ", ".#.   "),
            ([4], " ###.   ", "####.   "),  # clue = 4, empty = 1, black = 3 => white = 0
            ([2], "  #     ", ". #     "),  # clue = 2, empty = 2, black = 1 => white = 1
            ([2], "  ##    ", "..##    "),  # clue = 2, empty = 2, black = 2 => white = 2
            ([3], "   #    ", ".  #    "),  # clue = 3, empty = 3, black = 1 => white = 1
            ([3], "   ##   ", ".. ##   "),  # clue = 3, empty = 3, black = 2 => white = 2
            ([3], " ###    ", ".###    "),  # clue = 3, empty = 1, black = 3 => white = 1
            ([3], "  ###   ", "..###   "),  # clue = 3, empty = 2, black = 3 => white = 2
            ([4], "  ##    ", "  ##    "),  # clue = 4, empty = 2, black = 2 => white = 0
            (
                [2, 7, 3, 3, 7, 6, 9],
                "                   #             #       #        #        .",
                "                   #             #       #        #        .",
            ),
        ],
    )
    def test_left_to_right(self, clues, line, outcome):
        assert MercuryEdgeRule.apply_left_to_right(LineClue(clues), LineView(line)) == LineView(
            outcome
        )
