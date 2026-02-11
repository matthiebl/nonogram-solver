from nonogram.core import CellState, LineClue, LineView
from nonogram.exceptions import LineTooShortContradiction


def black_runs(state: LineView) -> list[tuple[int, int]]:
    """Returns a list of the sequences of black cells.

    Args:
        state (LineView): A given line state

    Returns:
        list[tuple[int, int]]: A list of (start index, length) pairs
    """
    runs = []
    pos = 0
    n = len(state)

    while pos < n:
        if state[pos] == CellState.BLACK:
            start = pos
            while pos < n and state[pos] == CellState.BLACK:
                pos += 1
            runs.append((start, pos - start))
        else:
            pos += 1

    return runs


def earliest_starts(clues: LineClue, state: LineView) -> list[int]:
    """Returns the indices of the earliest start to each clue.
    Ignores some aspects of current cells, other than completely impossible

    Raises:
        LineTooShortContradiction: When unable to find a place for all clues

    Returns:
        list[int]: A list of earliest indices for the left of each clue
    """
    starts = []
    pos = 0
    for clue in clues:
        while True:
            if pos + clue > len(state):
                raise LineTooShortContradiction(pos, clue, len(state))
            if (
                all(state[pos + i] in (CellState.BLACK, CellState.UNKNOWN) for i in range(clue))
                and (pos == 0 or state[pos - 1] != CellState.BLACK)
                and (pos + clue == len(state) or state[pos + clue] != CellState.BLACK)
            ):
                break
            pos += 1

        starts.append(pos)
        pos += clue + 1

    return starts


def latest_starts(clues: LineClue, state: LineView) -> list[int]:
    """Returns the indices of the latest start to each clue.
    Ignores some aspects of current cells, other than completely impossible

    Raises:
        LineTooShortContradiction: When unable to find a place for all clues

    Returns:
        list[int]: A list of latest indices for the left of each clue
    """
    starts = []
    pos = len(state)

    for clue in reversed(clues):
        pos -= clue
        while True:
            if pos < 0:
                raise LineTooShortContradiction()
            if (
                all(state[pos + i] in (CellState.BLACK, CellState.UNKNOWN) for i in range(clue))
                and (pos + clue == len(state) or state[pos + clue] != CellState.BLACK)
                and (pos == 0 or state[pos - 1] != CellState.BLACK)
            ):
                break
            pos -= 1

        starts.append(pos)
        pos -= 1

    return list(reversed(starts))
