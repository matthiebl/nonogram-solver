import pytest

from nonogram.core import CellState, Grid, LineClue, LineView
from nonogram.exceptions import Contradiction


class TestCellState:
    def test_of_method(self):
        assert CellState.of("#") == CellState.BLACK
        assert CellState.of(".") == CellState.WHITE
        assert CellState.of(" ") == CellState.UNKNOWN

        with pytest.raises(TypeError):
            CellState.of("a")
        with pytest.raises(TypeError):
            CellState.of(1)


class TestLineClue:
    def test_basic_usage(self):
        """
        Test basic extension of base type tuple[int] works as expected
        """
        clues = LineClue([1, 2, 3])
        assert len(clues) == 3
        assert list(clues) == [1, 2, 3]
        assert all(a == b for a, b in zip(clues, [1, 2, 3]))
        assert clues[2] == 3

    @pytest.mark.parametrize("init", [1, "a", ["a"], ("a",)])
    def test_invalid_types(self, init):
        """
        Invalid types should raise exception
        """
        with pytest.raises(TypeError):
            LineClue(init)


class TestLineView:
    def test_basic_usage(self):
        """
        Test basic extension of base type list[CellState] works as expected
        """
        line1 = LineView("##. ")
        assert len(line1) == 4
        assert list(line1) == [CellState.BLACK, CellState.BLACK, CellState.WHITE, CellState.UNKNOWN]
        assert line1[0] == CellState.BLACK
        assert line1[-1] == CellState.UNKNOWN

        line2 = LineView([CellState.BLACK, CellState.BLACK, CellState.WHITE, CellState.UNKNOWN])
        assert len(line2) == 4
        assert list(line2) == [CellState.BLACK, CellState.BLACK, CellState.WHITE, CellState.UNKNOWN]
        assert line2[0] == CellState.BLACK
        assert line2[-1] == CellState.UNKNOWN

        assert line1 == line2

    @pytest.mark.parametrize("init", [1, "a", ["a"], ("a",), [1, 2, 3], ".#123"])
    def test_invalid_types(self, init):
        """
        Invalid types should raise exception
        """
        with pytest.raises(TypeError):
            LineView(init)

    def test_str_representation(self):
        assert str(LineView("#. ")) == "#. "
        assert str(LineView([CellState.BLACK, CellState.WHITE, CellState.UNKNOWN])) == "#. "

    def test_state_method(self):
        line = LineView("#. ")
        assert line.state() == (CellState.BLACK, CellState.WHITE, CellState.UNKNOWN)

    # def test_apply_method(self):
    #     line = LineView("#. ")
    #     assert not line.apply(LineView("#. "))
    #     assert line == LineView("#. ")

    #     assert line.apply(LineView("#.."))
    #     assert line == LineView("#..")

    #     line2 = LineView("     ")
    #     assert line2.apply(LineView(".    "))
    #     assert line2.apply(LineView(" .   "))
    #     assert line2.apply(LineView("  #  "))
    #     assert line2.apply(LineView(".  # "))

    #     assert line2 == LineView("..## ")

    # @pytest.mark.parametrize(
    #     "init, update",
    #     [
    #         ("#. ", ".  "),
    #         ("#. ", " # "),
    #         ("#. ", "## "),
    #         ("#. ", ".# "),
    #         ("#. ", ""),
    #         ("#. ", "#."),
    #         ("#. ", "#.  "),
    #     ],
    # )
    # def test_apply_method_contradictions(self, init, update):
    #     line = LineView(init)
    #     with pytest.raises(Contradiction):
    #         line.apply(LineView(update))


class TestGrid:
    def test_small_grid(self):
        grid = Grid(width=2, height=2)
        grid.apply_row(0, LineView("##"))
        assert not grid.is_solved()
