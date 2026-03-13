from nonogram.core import Cell, Clues, LineState
from nonogram.rules import SplitRule
from nonogram.rules.overlap_rules import black_runs, earliest_starts, latest_starts


class CompleteEdgeSplitRule(SplitRule):
    """Splits a line at fully-determined prefix/suffix blocks into independent segments.
    Allows solving each segment independently, then merging results back together."""

    def split(self, clues: Clues, state: LineState) -> tuple[tuple[Clues, LineState], ...]:
        if state.is_complete() or not clues:
            return ((clues, state),)

        splits = []

        left_clues, left_state, remaining_clues, remaining_state = consume_complete_prefix(
            clues, state
        )

        if left_state:
            splits.append((left_clues, left_state))

        right_clues, right_state, final_clues, final_state = consume_complete_prefix(
            Clues(remaining_clues[::-1]), LineState(remaining_state[::-1])
        )

        splits.append((Clues(final_clues[::-1]), LineState(final_state[::-1])))

        if right_state:
            splits.append((Clues(right_clues[::-1]), LineState(right_state[::-1])))

        return tuple(splits)

    def merge(self, segments: tuple[LineState, ...]) -> LineState:
        merged: list[Cell] = []
        for segment in segments:
            merged.extend(segment)
        return LineState(merged)


class CrossBoundedSplitRule(SplitRule):
    """Splits a line at a cross cell when the clue assignment to each side is unambiguous.
    All clues 0..j that must end before the cross go left; the rest go right. Each side
    is then solved independently, enabling tighter deductions on the sub-problems."""

    def split(self, clues: Clues, state: LineState) -> tuple[tuple[Clues, LineState], ...]:
        if not clues or state.is_complete():
            return ((clues, state),)

        latest = latest_starts(clues, state)
        earliest = earliest_starts(clues, state)

        for p, cell in enumerate(state):
            if cell != Cell.CROSS:
                continue

            # Find maximal j such that clues 0..j all end at or before p in their
            # latest valid position. Since latest is monotone, we can break early.
            j = -1
            for k in range(len(clues)):
                if latest[k] + clues[k] <= p:
                    j = k
                else:
                    break

            if j < 0:
                continue

            # The first right-side clue (j+1) must be forced past p; if it can
            # still start at or before p the assignment is ambiguous and we skip.
            if j + 1 < len(clues) and earliest[j + 1] <= p:
                continue

            # Guard: each side must have enough clues to cover its BOX runs.
            # latest_starts can return positions that leave BOX cells uncovered,
            # so a split where one side has more BOX runs than allocated clues is invalid.
            left_state = LineState(state[: p + 1])
            right_state = LineState(state[p + 1 :])
            if len(black_runs(left_state)) > j + 1:
                continue
            if len(black_runs(right_state)) > len(clues) - j - 1:
                continue

            # Clues 0..j go left (state[:p+1] includes the cross as a boundary),
            # clues j+1..n-1 go right.
            return (
                (Clues(clues[: j + 1]), left_state),
                (Clues(clues[j + 1 :]), right_state),
            )

        return ((clues, state),)

    def merge(self, segments: tuple[LineState, ...]) -> LineState:
        merged: list[Cell] = []
        for segment in segments:
            merged.extend(segment)
        return LineState(merged)


def consume_complete_prefix(
    clues: Clues, state: LineState
) -> tuple[Clues, LineState, Clues, LineState]:
    """
    Consumes fully-complete blocks from the left edge.
    Returns:
        consumed_clues, consumed_state,
        remaining_clues, remaining_state
    """
    i = 0
    n = len(state)
    consumed_clues = []
    remaining_clues = list(clues)

    while remaining_clues:
        while i < n and state[i] == Cell.CROSS:
            i += 1

        if i >= n or state[i] != Cell.BOX:
            break

        black_start = i
        while i < n and state[i] == Cell.BOX:
            i += 1
        black_length = i - black_start

        if black_length != remaining_clues[0] or i >= n or state[i] != Cell.CROSS:
            i = black_start
            break

        consumed_clues.append(remaining_clues.pop(0))
        i += 1

    return (
        Clues(consumed_clues),
        LineState(state[:i]),
        Clues(remaining_clues),
        LineState(state[i:]),
    )
