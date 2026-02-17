from functools import lru_cache
from math import comb

from nonogram.core import CellState, LineClue, LineView
from nonogram.exceptions import EnumerationContradiction
from nonogram.rules import Rule


class EnumerationRule(Rule):
    cost = "HIGH"

    @staticmethod
    def apply(clues: LineClue, state: LineView) -> LineView:
        complexity = line_complexity(clues, len(state))
        if complexity > 50_000:
            return state

        possibilities = enumerate_possibilities(clues, state)
        if not possibilities:
            raise EnumerationContradiction(f"Cannot enumerate {clues}: {state}")

        result = []
        for cell_options in zip(*possibilities):
            vals = set(cell_options)
            result.append(vals.pop() if len(vals) == 1 else CellState.UNKNOWN)

        return LineView(result)


@lru_cache(maxsize=10_000)
def enumerate_possibilities(clues: LineClue, state: LineView) -> tuple[LineView, ...]:
    if state.is_complete():
        return (state,)

    if not clues:
        if CellState.BLACK in state:
            return ()
        return (LineView([CellState.WHITE] * len(state)),)

    options = []
    clue, *rest = list(clues)
    min_rest = sum(rest) + len(rest)

    for start in range(len(state) - clue - min_rest + 1):
        prefix = [CellState.WHITE] * start + [CellState.BLACK] * clue
        if start + clue < len(state):
            prefix += [CellState.WHITE]

        if any(state[i] not in (CellState.UNKNOWN, prefix[i]) for i in range(len(prefix))):
            continue

        for tail in enumerate_possibilities(LineClue(rest), LineView(state[len(prefix) :])):
            options.append(LineView(prefix + list(tail)))

    return tuple(options)


def line_complexity(clues: LineClue, length: int) -> float:
    k = len(clues)
    if k == 0:
        return 1
    slack = length - (sum(clues) + k - 1)
    if slack < 0:
        return float("inf")
    return comb(slack + k, k)
