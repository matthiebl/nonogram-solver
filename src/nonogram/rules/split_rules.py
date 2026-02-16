from nonogram.core import CellState, LineClue, LineView
from nonogram.rules import SplitRule
from nonogram.rules.utils import black_runs


class CompleteEdgeSplitRule(SplitRule):
    @staticmethod
    def apply(clues: LineClue, state: LineView) -> tuple[tuple[LineClue, LineView]]:
        if state.is_complete() or not clues:
            return ((clues, state),)

        splits = []

        left_clues, left_state, remaining_clues, remaining_state = consume_complete_prefix(
            clues, state
        )

        if left_state:
            splits.append((left_clues, left_state))

        right_clues, right_state, final_clues, final_state = consume_complete_prefix(
            LineClue(remaining_clues[::-1]), LineView(remaining_state[::-1])
        )

        splits.append((LineClue(final_clues[::-1]), LineView(final_state[::-1])))

        if right_state:
            splits.append((LineClue(right_clues[::-1]), LineView(right_state[::-1])))

        return tuple(splits)


def consume_complete_prefix(
    clues: LineClue, state: LineView
) -> tuple[LineClue, LineView, LineClue, LineView]:
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
        while n and state[i] == CellState.WHITE:
            i += 1

        if i >= n or state[i] != CellState.BLACK:
            break

        black_start = i
        while i < n and state[i] == CellState.BLACK:
            i += 1
        black_length = i - black_start

        if black_length != clues[0]:
            break

        if i < n and state[i] != CellState.WHITE:
            break

        consumed_clues.append(remaining_clues.pop(0))
        i += 1

    return (
        LineClue(consumed_clues),
        LineView(state[:i]),
        LineClue(remaining_clues),
        LineView(state[i:]),
    )
