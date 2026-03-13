from nonogram.core import Cell, Clues, LineState
from nonogram.rules import Rule


class CompleteCluesRule(Rule):
    """If the existing black runs already match the clues exactly, fill all remaining
    unknowns with crosses. Early termination when all clues are successfully placed."""

    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        black = [length for _, length in black_runs(state)]

        if list(clues) != black:
            return state

        new = LineState(state)
        for i, cell in enumerate(state):
            if cell != Cell.BOX:
                new[i] = Cell.CROSS

        return new


class FirstClueGapRule(Rule):
    """Handles the edge case where the first or last clue has only one position.
    If a black run matches the clue length with exactly one empty cell of space, that cell
    must be a cross."""

    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        runs = black_runs(state)

        if not runs or not clues or state.is_complete():
            return state

        new = LineState(state)

        first_clue = clues[0]
        pos, length = runs[0]
        white = pos
        if first_clue == white - 1 == length:
            new[pos - 1] = Cell.CROSS

        last_clue = clues[-1]
        pos, length = runs[-1]
        white = len(state) - (pos + length)
        if last_clue == white - 1 == length:
            new[pos + length] = Cell.CROSS

        return new


class GapTooSmallRule(Rule):
    """Marks a contiguous gap of unknowns as crosses when it is too short to fit any clue.
    A gap bounded by crosses (or edges) that is smaller than the minimum clue must be empty."""

    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        if not clues or state.is_complete():
            return state

        min_clue = min(clues)
        new = LineState(state)
        n = len(state)
        i = 0

        while i < n:
            if state[i] != Cell.UNKNOWN:
                i += 1
                continue

            gap_start = i
            while i < n and state[i] == Cell.UNKNOWN:
                i += 1
            gap_len = i - gap_start

            left_ok = gap_start == 0 or state[gap_start - 1] == Cell.CROSS
            right_ok = i == n or state[i] == Cell.CROSS

            if left_ok and right_ok and gap_len < min_clue:
                for j in range(gap_start, gap_start + gap_len):
                    new[j] = Cell.CROSS

        return new


def black_runs(state: LineState) -> list[tuple[int, int]]:
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
        if state[pos] == Cell.BOX:
            start = pos
            while pos < n and state[pos] == Cell.BOX:
                pos += 1
            runs.append((start, pos - start))
        else:
            pos += 1

    return runs
