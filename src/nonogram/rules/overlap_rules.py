from nonogram.core import Cell, Clues, LineState
from nonogram.exceptions import CellConflictContradiction, LineTooShortContradiction
from nonogram.rules import Rule
from nonogram.rules.simple_rules import black_runs


class OverlapRule(Rule):
    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        if not clues or state.is_complete():
            return state

        earliest = earliest_starts(clues, state)
        latest = latest_starts(clues, state)

        new = LineState(state)

        for clue, early, late in zip(clues, earliest, latest):
            start = max(early, late)
            end = min(early + clue, late + clue)

            for i in range(start, end):
                if new[i] == Cell.CROSS:
                    raise CellConflictContradiction()
                new[i] = Cell.BOX

        return new


class NeverBlackRule(Rule):
    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        if not clues or state.is_complete():
            return state

        earliest = earliest_starts(clues, state)
        latest = latest_starts(clues, state)

        coverage = [False] * len(state)

        for clue, early, late in zip(clues, earliest, latest):
            for i in range(early, late + clue):
                coverage[i] = True

        new = LineState(state)
        for i, can_be_black in enumerate(coverage):
            if not can_be_black:
                if state[i] == Cell.BOX:
                    raise CellConflictContradiction(
                        "Overlap suggests cell can never be black", clues, state
                    )
                new[i] = Cell.CROSS

        return new


class MinimumLengthExpansionRule(Rule):
    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        n = len(state)
        new_state = LineState(state)

        if not clues or state.is_complete():
            return new_state

        earliest = earliest_starts(clues, state)
        latest = latest_starts(clues, state)

        runs = black_runs(state)

        for run_start, run_len in runs:
            left_bounded = run_start == 0 or state[run_start - 1] == Cell.CROSS
            right_end = run_start + run_len
            right_bounded = right_end == n or state[right_end] == Cell.CROSS

            if not (left_bounded or right_bounded) or (left_bounded and right_bounded):
                continue

            # Find candidate clue(s) that could cover this run
            possible_clues = set()
            for i, clue_len in enumerate(clues):
                s_earliest = earliest[i]
                s_latest = latest[i]
                if s_earliest <= run_start <= s_latest + clue_len - 1:
                    possible_clues.add(clues[i])

            if not possible_clues:
                continue

            required_length = min(possible_clues)
            start = run_start if left_bounded else run_start + run_len - required_length
            for i in range(start, start + required_length):
                if i >= n or new_state[i] == Cell.CROSS:
                    raise CellConflictContradiction()
                new_state[i] = Cell.BOX

            if len(possible_clues) == 1:
                if start - 1 >= 0:
                    new_state[start - 1] = Cell.CROSS
                if start + required_length < n:
                    new_state[start + required_length] = Cell.CROSS

        return new_state


def earliest_starts(clues: Clues, state: LineState) -> list[int]:
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
                raise LineTooShortContradiction()

            if (
                any(state[i] == Cell.CROSS for i in range(pos, pos + clue))
                or (pos > 0 and state[pos - 1] == Cell.BOX)
                or (pos + clue < len(state) and state[pos + clue] == Cell.BOX)
            ):
                pos += 1
                continue

            # Accept placement
            break

        starts.append(pos)
        pos += clue + 1

    return starts


def latest_starts(clues: Clues, state: LineState) -> list[int]:
    """Returns the indices of the latest start to each clue.
    Ignores some aspects of current cells, other than completely impossible

    Raises:
        LineTooShortContradiction: When unable to find a place for all clues

    Returns:
        list[int]: A list of latest indices for the left of each clue
    """
    n = len(state)

    # Reverse everything
    rev_state = LineState(state[::-1])
    rev_clues = Clues(clues[::-1])
    rev_starts = earliest_starts(rev_clues, rev_state)

    # Map reversed starts back to original indices
    return [n - (start + clue) for start, clue in zip(rev_starts, rev_clues)][::-1]
