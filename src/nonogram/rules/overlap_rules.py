from nonogram.core import CellState, LineClue, LineView
from nonogram.exceptions import CellConflictContradiction, LineTooShortContradiction
from nonogram.rules import Rule
from nonogram.rules.simple_rules import black_runs


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


class MinimumLengthExpansionRule(Rule):
    @staticmethod
    def apply(clues: LineClue, state: LineView) -> LineView:
        n = len(state)
        new_state = LineView(state)

        if not clues or state.is_complete():
            return new_state

        earliest = earliest_starts(clues, state)
        latest = latest_starts(clues, state)

        runs = black_runs(state)

        for run_start, run_len in runs:
            left_bounded = run_start == 0 or state[run_start - 1] == CellState.WHITE
            right_end = run_start + run_len
            right_bounded = right_end == n or state[right_end] == CellState.WHITE

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
                if i >= n or new_state[i] == CellState.WHITE:
                    raise CellConflictContradiction()
                new_state[i] = CellState.BLACK

            if len(possible_clues) == 1:
                if start - 1 >= 0:
                    new_state[start - 1] = CellState.WHITE
                if start + required_length < n:
                    new_state[start + required_length] = CellState.WHITE

        return new_state


def earliest_starts(clues: LineClue, state: LineView) -> list[int]:
    """Returns the indices of the earliest start to each clue.
    Ignores some aspects of current cells, other than completely impossible

    Raises:
        LineTooShortContradiction: When unable to find a place for all clues

    Returns:
        list[int]: A list of earliest indices for the left of each clue
    """

    runs = black_runs(state)
    run_idx = 0
    starts = []
    pos = 0

    for clue in clues:
        while True:
            if pos + clue > len(state):
                raise LineTooShortContradiction()

            if any(state[i] == CellState.WHITE for i in range(pos, pos + clue)):
                pos += 1
                continue

            segment = (pos, pos + clue)
            intersecting = list(runs_intersecting(runs, *segment))

            # Reject partial run coverage
            if any(
                not (pos <= r_start and r_start + r_len <= pos + clue)
                for r_start, r_len in intersecting
            ):
                pos += 1
                continue

            # Reject if touching black outside segment
            if (pos > 0 and state[pos - 1] == CellState.BLACK) or (
                pos + clue < len(state) and state[pos + clue] == CellState.BLACK
            ):
                pos += 1
                continue

            # Accept placement
            break

        starts.append(pos)

        # Consume fully covered runs
        while run_idx < len(runs):
            r_start, r_len = runs[run_idx]
            if r_start >= pos + clue:
                break
            run_idx += 1

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
    n = len(state)

    # Reverse everything
    rev_state = LineView(state[::-1])
    rev_clues = LineClue(clues[::-1])
    rev_starts = earliest_starts(rev_clues, rev_state)

    # Map reversed starts back to original indices
    return [n - (start + clue) for start, clue in zip(rev_starts, rev_clues)][::-1]


def runs_intersecting(runs: list[tuple[int, int]], start: int, end: int):
    """Returns runs that intersect [start, end)."""
    for r_start, r_len in runs:
        r_end = r_start + r_len
        if not (r_end <= start or r_start >= end):
            yield (r_start, r_len)


def is_closed_run(state: LineView, start: int, length: int) -> bool:
    left_closed = start == 0 or state[start - 1] == CellState.WHITE
    right_end = start + length
    right_closed = right_end == len(state) or state[right_end] == CellState.WHITE
    return left_closed and right_closed
