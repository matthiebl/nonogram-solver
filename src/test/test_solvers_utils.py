from pixelpuzzle.solvers.utils import create_possibilities, deduce_empty_line, increment_state


def test_deduce_empty_line_len_5():
    assert deduce_empty_line(5, []) == "....."
    assert deduce_empty_line(5, [1]) == "     "
    assert deduce_empty_line(5, [1, 1]) == "     "
    assert deduce_empty_line(5, [1, 1, 1]) == "#.#.#"
    assert deduce_empty_line(5, [2]) == "     "
    assert deduce_empty_line(5, [2, 1]) == " #   "
    assert deduce_empty_line(5, [1, 2]) == "   # "
    assert deduce_empty_line(5, [3]) == "  #  "
    assert deduce_empty_line(5, [3, 1]) == "###.#"
    assert deduce_empty_line(5, [1, 3]) == "#.###"
    assert deduce_empty_line(5, [4]) == " ### "
    assert deduce_empty_line(5, [5]) == "#####"


def test_deduce_empty_line_longer():
    assert deduce_empty_line(13, [3, 1, 5]) == "  #     ###  "


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
