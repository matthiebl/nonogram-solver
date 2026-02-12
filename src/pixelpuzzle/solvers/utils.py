from collections import deque

from pixelpuzzle.exceptions import PixelIterationError, PixelMergeError
from pixelpuzzle.utils import Square


def merge_states(left: str, right: str) -> str:
    """
    Given two states, merges them together. Similar to an OR operation.
    """
    state = ""
    for a, b in zip(left, right):
        if a == Square.BLANK:
            state += b
        elif b == Square.BLANK:
            state += a
        elif a != b:
            raise PixelMergeError(f"Cannot merge two different known states: {a} != {1}")
        else:
            state += a
    return state


def increment_empty_line(clues: list[int], state: str) -> str:
    """
    Increments a single line purely on clues, ignoring assistance from current state.
    """
    length = len(state)
    if not clues:
        return merge_states(state, Square.WHITE * length)

    known_length = sum(clues) + len(clues) - 1
    gap = length - known_length

    if gap == 0:
        result = Square.BLACK * clues[0]
        for clue in clues[1:]:
            result += Square.WHITE + Square.BLACK * clue
        return merge_states(state, result)

    left = []
    for i, clue in enumerate(clues[:-1], start=1):
        left += [i] * clue + [0]
    left += [len(clues)] * clues[-1] + [0] * gap

    right = [0] * gap + [1] * clues[0]
    for i, clue in enumerate(clues[1:], start=2):
        right += [0] + [i] * clue

    deduced = "".join(
        [Square.BLACK if a > 0 and a == b else Square.BLANK for a, b in zip(left, right)]
    )
    return merge_states(state, deduced)


def create_possibilities(clues: tuple[int], mask: str) -> tuple[str]:
    if not clues:
        if mask.count(Square.BLACK) > 0:
            return tuple()
        return (Square.WHITE * len(mask),)

    options = []

    (clue, *remaining_clues) = clues
    leave = sum(remaining_clues) + len(remaining_clues)
    for white in range(len(mask) - leave - clue + 1):
        prefix = Square.WHITE * white + Square.BLACK * clue
        if len(prefix) != len(mask):
            prefix += Square.WHITE
        if not all(m == p or m == Square.BLANK for m, p in zip(mask, prefix)):
            continue
        possibilities = create_possibilities(
            tuple(remaining_clues),
            mask[len(prefix) :],
        )
        if not possibilities:
            continue
        options += [prefix + p for p in possibilities]

    return tuple(option for option in options)


def increment_state(clues: tuple[int], state: str) -> str:
    # state = increment_state_from_edge(clues, state)

    # i, j = state.index(Square.BLANK), state[::-1].index(Square.BLANK) - 1

    # left = state[: state.index(Square.BLANK)]
    # right = state[:]

    # queue = deque(state)
    # left, right = "", ""
    # while queue[0] != Square.BLANK:
    #     left += queue.popleft()
    # while queue[-1] != Square.BLANK:
    #     right = queue.pop() + right
    # state = "".join(queue)

    possibilities = create_possibilities(clues, state)
    if len(possibilities) == 0:
        raise PixelIterationError("State does not comply with clues", clues, state)

    probabilities = {i: {Square.BLACK: 0, Square.WHITE: 0} for i in range(len(state))}
    for option in possibilities:
        for i, c in enumerate(option):
            probabilities[i][c] += 1

    return "".join(
        Square.BLACK
        if chance[Square.WHITE] == 0
        else Square.WHITE
        if chance[Square.BLACK] == 0
        else Square.BLANK
        for chance in probabilities.values()
    )


def increment_state_from_edge(clues: tuple[int], state: str) -> str:
    """
    Increment inward from the edges.
    """
    left, middle, right = split_from_edge(state)

    left = deque(left)
    while True:
        while left[0] == Square.WHITE:
            left.popleft()

    while clues[0] <= left.count(Square.BLACK):
        left.replace(Square.BLACK, Square.WHITE, clues[0])
        clues = clues[1:]
        print(clues)
    while left and left[0] == Square.WHITE:
        left = left[1:]
    print(left, clues)
    return clues, left, middle, right


def reduce_known_clues_state(clues: tuple[int], state: str) -> tuple[tuple[int], str]:
    # left side
    runs = black_runs(state)
    while clues and runs:
        if runs[0][1] == clues:
            pass


def black_runs(state: str) -> list[tuple[int, int]]:
    """
    Returns a list of (start, length) for each contiguous run of '#'.
    """
    runs = []
    i = 0
    n = len(state)

    while i < n:
        if state[i] == Square.BLACK:
            start = i
            while i < n and state[i] == Square.BLACK:
                i += 1
            runs.append((start, i - start))
        else:
            i += 1

    return runs


def split_from_edge(state: str) -> tuple[str, str, str]:
    queue = deque(state)
    left, right = "", ""
    while queue and queue[0] != Square.BLANK:
        left += queue.popleft()
    while queue and queue[-1] != Square.BLANK:
        right = queue.pop() + right
    return left, "".join(queue), right
