import pytest

from nonogram.core import LineView
from nonogram.rules.simple_rules import CompleteCluesRule, FirstClueGapRule, black_runs
from tst.nonogram.utils import RuleTester


class TestBlackRuns:
    @pytest.mark.parametrize(
        "state, expected",
        [
            ("", []),
            (".", []),
            (" ", []),
            ("....", []),
            ("###", [(0, 3)]),
            ("# #", [(0, 1), (2, 1)]),
            ("#.#", [(0, 1), (2, 1)]),
            ("#..", [(0, 1)]),
            (" #.", [(1, 1)]),
            (" ###  .. #.. ##.   #", [(1, 3), (9, 1), (13, 2), (19, 1)]),
        ],
    )
    def test_basic_usage(self, state, expected):
        assert black_runs(LineView(state)) == expected


class TestCompleteCluesRule:
    tester = RuleTester(CompleteCluesRule)

    @pytest.mark.parametrize(
        "clues, state, expected",
        [
            ((1,), "      ", "      "),
            ((1,), " #    ", ".#...."),
            ((1,), " #.  .", ".#...."),
            ((2,), " ##   ", ".##..."),
            ((2,), " ##   ", ".##..."),
            ((2, 1), " ##    # ", ".##....#."),
        ],
    )
    def test_apply(self, clues, state, expected):
        self.tester.assert_apply(clues, state, expected)


class TestFirstClueGapRule:
    tester = RuleTester(FirstClueGapRule)

    @pytest.mark.parametrize(
        "clues, state, expected",
        [
            ((1,), " #       ", " #       "),
            ((1,), "  #       ", " .#       "),
            ((1,), "       #  ", "       #. "),
            ((2,), "   ##     ", "  .##     "),
            ((2,), "     ##   ", "     ##.  "),
            ((1, 3), "  # #     ", " .# #     "),
        ],
    )
    def test_apply(self, clues, state, expected):
        self.tester.assert_apply(clues, state, expected)
