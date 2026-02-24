import pytest

from nonogram.core import Cell, Clues, Grid, LineState


class TestCellState:
    def test_of_method(self):
        assert Cell.of("#") == Cell.BOX
        assert Cell.of(".") == Cell.CROSS
        assert Cell.of(" ") == Cell.UNKNOWN

        with pytest.raises(TypeError):
            Cell.of("a")
        with pytest.raises(TypeError):
            Cell.of(1)


class TestLineClue:
    def test_basic_usage(self):
        """
        Test basic extension of base type tuple[int] works as expected
        """
        clues = Clues([1, 2, 3])
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
            Clues(init)


class TestLineView:
    def test_basic_usage(self):
        """
        Test basic extension of base type list[CellState] works as expected
        """
        line1 = LineState("##. ")
        assert len(line1) == 4
        assert list(line1) == [Cell.BOX, Cell.BOX, Cell.CROSS, Cell.UNKNOWN]
        assert line1[0] == Cell.BOX
        assert line1[-1] == Cell.UNKNOWN

        line2 = LineState([Cell.BOX, Cell.BOX, Cell.CROSS, Cell.UNKNOWN])
        assert len(line2) == 4
        assert list(line2) == [Cell.BOX, Cell.BOX, Cell.CROSS, Cell.UNKNOWN]
        assert line2[0] == Cell.BOX
        assert line2[-1] == Cell.UNKNOWN

        assert line1 == line2

    def test_init_copy(self):
        line = LineState(".# ")
        copy = LineState(line)
        assert line == copy
        assert line is not copy
        copy[0] = Cell.BOX
        assert line[0] == Cell.CROSS
        assert copy[0] == Cell.BOX

    @pytest.mark.parametrize("init", [1, "a", ["a"], ("a",), [1, 2, 3], ".#123"])
    def test_invalid_types(self, init):
        """
        Invalid types should raise exception
        """
        with pytest.raises(TypeError):
            LineState(init)

    def test_str_representation(self):
        assert str(LineState("#. ")) == "#. "
        assert str(LineState([Cell.BOX, Cell.CROSS, Cell.UNKNOWN])) == "#. "

    def test_state_method(self):
        line = LineState("#. ")
        assert line.state() == (Cell.BOX, Cell.CROSS, Cell.UNKNOWN)

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
        grid.apply_row(0, LineState("##"))
        assert not grid.is_solved()
