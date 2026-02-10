import pytest

from pixelpuzzle.solvers.utils import black_runs, split_from_edge


class TestMergeState:
    pass


class TestBlackRuns:
    @pytest.mark.parametrize(
        "state, result",
        [
            ("", []),
            (".", []),
            (" ", []),
            ("#", [(0, 1)]),
            (".#", [(1, 1)]),
            ("#.", [(0, 1)]),
            ("# ", [(0, 1)]),
            ("##", [(0, 2)]),
            ("  ## ", [(2, 2)]),
            ("  # # ", [(2, 1), (4, 1)]),
            ("  # ## ", [(2, 1), (4, 3)]),
            (". #.##.", [(2, 1), (4, 3)]),
        ],
    )
    def test_basic(self, state, result):
        assert black_runs(state) == result


class TestSplitFromEdge:
    @pytest.mark.parametrize(
        "state, result",
        [
            ("", ["", "", ""]),
            (".", [".", "", ""]),
            ("#", ["#", "", ""]),
            (" ", ["", " ", ""]),
        ],
    )
    def test_basic(self, state, result):
        assert split_from_edge(state) == result
