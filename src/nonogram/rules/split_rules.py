from nonogram.core import Cell, Clues, LineState
from nonogram.rules import SplitRule


class CompleteEdgeSplitRule(SplitRule):
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
