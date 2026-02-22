import pytest

from nonogram.rules.edge_rules import GlueEdgeRule, MercuryEdgeRule
from tst.nonogram.utils import EdgeRuleTester


class TestGlueEdgeRule:
    tester = EdgeRuleTester(GlueEdgeRule)

    @pytest.mark.parametrize(
        "clues, state, expected",
        [
            ((2,), "#    ", "##..."),
            ((2,), ".#    ", ".##..."),
            ((2, 1), ".#    ", ".##.  "),
            ((2, 3, 1), ".# . #     ", ".##. ##    "),
            (
                (7, 9, 2),
                "       .#######  ..                               ",
                "       .#######  ..                               ",
            ),
        ],
    )
    def test_left_to_right(self, clues, state, expected):
        self.tester.assert_apply_left_to_right(clues, state, expected)

    @pytest.mark.parametrize(
        "clues, state, expected",
        [
            ((2,), "#    ", "##..."),
            ((2,), ".#    ", ".##..."),
            ((2, 1), ".#    ", ".##.  "),
            ((2, 3, 1), ".# . #     ", ".##. ##    "),
        ],
    )
    def test_apply(self, clues, state, expected):
        self.tester.assert_apply(clues, state, expected)


class TestMercuryEdgeRule:
    tester = EdgeRuleTester(MercuryEdgeRule)

    @pytest.mark.parametrize(
        "clues, state, expected",
        [
            ((1,), " #    ", ".#    "),
            ((1,), " #.   ", ".#.   "),
            ((4,), " ###.   ", "####.   "),
            ((2,), "  #     ", ". #     "),
            ((2,), "  ##    ", "..##    "),
            ((3,), "   #    ", ".  #    "),
            ((3,), "   ##   ", ".. ##   "),
            ((3,), " ###    ", ".###    "),
            ((3,), "  ###   ", "..###   "),
            ((4,), "  ##    ", "  ##    "),
            (
                (2, 7, 3, 3, 7, 6, 9),
                "                   #             #       #        #        .",
                "                   #             #       #        #        .",
            ),
        ],
    )
    def test_left_to_right(self, clues, state, expected):
        self.tester.assert_apply_left_to_right(clues, state, expected)
