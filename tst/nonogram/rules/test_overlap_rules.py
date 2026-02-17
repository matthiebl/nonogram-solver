import pytest

from nonogram.core import LineClue, LineView
from nonogram.exceptions import Contradiction
from nonogram.rules.overlap_rules import earliest_starts, latest_starts


class TestEarliestStarts:
    @pytest.mark.parametrize(
        "clues, line, outcome",
        [
            ((), "", []),
            ((1,), " ", [0]),
            ((1,), "   ", [0]),
            ((1,), ". ", [1]),
            ((1,), ".. ", [2]),
            ((1,), ". #", [2]),
            ((2,), ". #", [1]),
            ((2,), ". ##", [2]),
            ((1, 2, 3), "        ", [0, 2, 5]),
            ((1, 3), ".  ..  #  ", [1, 5]),
            ((1, 3), ".  ..   #  ", [1, 6]),
        ],
    )
    def test_basic_usage(self, clues, line, outcome):
        assert earliest_starts(LineClue(clues), LineView(line)) == outcome

    @pytest.mark.parametrize(
        "clues, line",
        [
            ((1,), ""),
            ((2,), " "),
            ((2,), ". "),
            ((2,), " ."),
            ((2,), "#"),
            ((2,), "#"),
            ((1, 2, 3), ".       "),
            ((1, 2, 3), "       ."),
        ],
    )
    def test_contradictions(self, clues, line):
        with pytest.raises(Contradiction):
            earliest_starts(LineClue(clues), LineView(line))


class TestLatestStarts:
    @pytest.mark.parametrize(
        "clues, line, outcome",
        [
            ((), "", []),
            ((1,), " ", [0]),
            ((1,), "   ", [2]),
            ((1,), ". ", [1]),
            ((1,), ".. ", [2]),
            ((1,), ".# ", [1]),
            ((2,), ".# ", [1]),
            ((2,), ".## ", [1]),
            ((1, 2, 3), "        ", [0, 2, 5]),
            ((1, 3), ".  ..  #  ", [5, 7]),
            ((1, 3), ".  ..   #  ", [6, 8]),
        ],
    )
    def test_basic_usage(self, clues, line, outcome):
        assert latest_starts(LineClue(clues), LineView(line)) == outcome

    @pytest.mark.parametrize(
        "clues, line",
        [
            ((1,), ""),
            ((2,), " "),
            ((2,), ". "),
            ((2,), " ."),
            ((2,), "#"),
            ((2,), "#"),
            ((1, 2, 3), ".       "),
            ((1, 2, 3), "       ."),
        ],
    )
    def test_contradictions(self, clues, line):
        with pytest.raises(Contradiction):
            latest_starts(LineClue(clues), LineView(line))
