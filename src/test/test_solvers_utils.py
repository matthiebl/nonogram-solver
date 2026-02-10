import pytest

from pixelpuzzle.exceptions import PixelIterationError
from pixelpuzzle.solvers.utils import (
    create_possibilities,
    increment_empty_line,
    increment_state,
    increment_state_from_edge,
    split_from_edge,
)


def test_increment_empty_line_len_5():
    assert increment_empty_line([], "     ") == "....."
    assert increment_empty_line([1], "     ") == "     "
    assert increment_empty_line([1, 1], "     ") == "     "
    assert increment_empty_line([1, 1, 1], "     ") == "#.#.#"
    assert increment_empty_line([2], "     ") == "     "
    assert increment_empty_line([2, 1], "     ") == " #   "
    assert increment_empty_line([1, 2], "     ") == "   # "
    assert increment_empty_line([3], "     ") == "  #  "
    assert increment_empty_line([3, 1], "     ") == "###.#"
    assert increment_empty_line([1, 3], "     ") == "#.###"
    assert increment_empty_line([4], "     ") == " ### "
    assert increment_empty_line([5], "     ") == "#####"


def test_increment_empty_line_longer():
    assert increment_empty_line([3, 1, 5], "             ") == "  #     ###  "


def test_create_possibilities_no_clues():
    assert create_possibilities((), " ") == (".",)
    assert create_possibilities((), ".") == (".",)
    assert create_possibilities((), "#") == tuple()
    assert create_possibilities((), "  ") == ("..",)
    assert create_possibilities((), " .") == ("..",)
    assert create_possibilities((), "   #   ") == tuple()


def test_create_possibilities_basic():
    assert create_possibilities((1, 1), "     ") == (
        "#.#..",
        "#..#.",
        "#...#",
        ".#.#.",
        ".#..#",
        "..#.#",
    )

    assert create_possibilities((1, 1), "#    ") == (
        "#.#..",
        "#..#.",
        "#...#",
    )

    assert create_possibilities((1, 1), ".    ") == (
        ".#.#.",
        ".#..#",
        "..#.#",
    )

    assert create_possibilities((1, 1), ".   #") == (
        ".#..#",
        "..#.#",
    )


def test_create_possibilities_medium():
    assert create_possibilities((1, 1, 5, 1, 1), "    # #  . # . ") == ("#.#.#####..#..#",)

    assert create_possibilities((2, 1, 1, 4), "  .       ## ") == (
        "##.#.#..####.",
        "##.#.#...####",
        "##.#..#.####.",
        "##.#..#..####",
        "##.#...#.####",
        "##..#.#.####.",
        "##..#.#..####",
        "##..#..#.####",
        "##...#.#.####",
    )

    assert create_possibilities((8, 1), "   ######  .  .") == (
        ".########.#....",
        ".########...#..",
        ".########....#.",
        "..########..#..",
        "..########...#.",
        "...########.#..",
        "...########..#.",
    )


def test_create_possibilities_finished():
    assert create_possibilities((1,), "#   ") == ("#...",)


def test_increment_state_no_clues():
    assert increment_state((), "..  ") == "...."


def test_increment_state_basic():
    assert increment_state((5,), "     ") == "#####"
    assert increment_state((4,), "     ") == " ### "
    assert increment_state((3,), "     ") == "  #  "
    assert increment_state((2,), "     ") == "     "
    assert increment_state((2, 2), "     ") == "##.##"


def test_increment_state_medium():
    assert increment_state((2, 1, 1, 4), "  .       ## ") == "##.      ### "


def test_increment_state_finished():
    assert increment_state((1,), ".#  ") == ".#.."


def test_increment_state_broken():
    assert (
        increment_state((1, 18, 4, 1, 7, 4), "            ########                              ")
        == "            ########                              "
    )
    assert increment_state((3,), ".. ..         ") == ".....         "


def test_increment_problem_1():
    clues = (3, 2, 6, 1, 5, 1, 2, 4)
    initial_state = ".###.##. #####.   ####.####..####.."
    with pytest.raises(PixelIterationError):
        increment_state(clues, initial_state)


def test_increment_state_from_edge():
    assert increment_state_from_edge((3), "#     ")


def test_split_from_edge():
    assert split_from_edge("#. .#") == ("#.", " ", ".#")
    assert split_from_edge("#.   .#") == ("#.", "   ", ".#")
    assert split_from_edge(".   .#") == (".", "   ", ".#")
    assert split_from_edge(".   .####.#") == (".", "   ", ".####.#")
    assert split_from_edge("#  #") == ("#", "  ", "#")
    assert split_from_edge("##  #.") == ("##", "  ", "#.")
