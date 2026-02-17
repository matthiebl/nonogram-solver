import pytest

from nonogram.core import LineView
from nonogram.rules.simple_rules import black_runs


class TestBlackRuns:
    @pytest.mark.parametrize(
        "line, outcome",
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
    def test_basic_usage(self, line, outcome):
        assert black_runs(LineView(line)) == outcome
