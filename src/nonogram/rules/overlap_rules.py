from nonogram.core import CellState, LineClue, LineView
from nonogram.exceptions import CellConflictContradiction, LineTooShortContradiction
from nonogram.rules import Rule


class OverlapRule(Rule):
    @staticmethod
    def apply(clues: LineClue, state: LineView) -> LineView:
        if not clues or state.is_complete():
            return state

        earliest = earliest_starts(clues, state)
        latest = latest_starts(clues, state)

        new = LineView(state)

        for clue, early, late in zip(clues, earliest, latest):
            start = max(early, late)
            end = min(early + clue, late + clue)

            for i in range(start, end):
                if new[i] == CellState.WHITE:
                    raise CellConflictContradiction()
                new[i] = CellState.BLACK

        return new


class NeverBlackRule(Rule):
    @staticmethod
    def apply(clues: LineClue, state: LineView) -> LineView:
        if not clues or state.is_complete():
            return state

        earliest = earliest_starts(clues, state)
        latest = latest_starts(clues, state)

        coverage = [False] * len(state)

        for clue, early, late in zip(clues, earliest, latest):
            for i in range(early, late + clue):
                coverage[i] = True

        new = LineView(state)
        for i, can_be_black in enumerate(coverage):
            if not can_be_black:
                if state[i] == CellState.BLACK:
                    raise CellConflictContradiction(
                        "Overlap suggests cell can never be black", clues, state
                    )
                new[i] = CellState.WHITE

        return new


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
