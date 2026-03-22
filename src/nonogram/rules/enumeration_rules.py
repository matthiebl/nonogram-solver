from functools import lru_cache
from math import comb

from nonogram.core import Cell, Clues, LineState
from nonogram.exceptions import EnumerationContradiction
from nonogram.rules import Rule


class EnumerationRule(Rule):
    cost = "HIGH"

    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        complexity = line_complexity(clues, len(state))
        if complexity > 100_000_000:
            return state

        possibilities = enumerate_possibilities(clues, state)
        if not possibilities:
            raise EnumerationContradiction(f"Cannot enumerate {clues}: {state}")

        result = []
        for cell_options in zip(*possibilities):
            vals = set(cell_options)
            result.append(vals.pop() if len(vals) == 1 else Cell.UNKNOWN)

        return LineState(result)


@lru_cache(maxsize=10_000)
def enumerate_possibilities(clues: Clues, state: LineState) -> tuple[LineState, ...]:
    if not clues:
        if Cell.BOX in state:
            return ()
        return (LineState([Cell.CROSS] * len(state)),)

    if state.is_complete():
        if state.count(Cell.BOX) != sum(clues):
            return ()
        return (state,)

    options = []
    clue, *rest = list(clues)
    min_rest = sum(rest) + len(rest)

    for start in range(len(state) - clue - min_rest + 1):
        prefix = [Cell.CROSS] * start + [Cell.BOX] * clue
        if start + clue < len(state):
            prefix += [Cell.CROSS]

        if any(state[i] not in (Cell.UNKNOWN, prefix[i]) for i in range(len(prefix))):
            continue

        for tail in enumerate_possibilities(Clues(rest), LineState(state[len(prefix) :])):
            options.append(LineState(prefix + list(tail)))

    return tuple(options)


def line_complexity(clues: Clues, length: int) -> float:
    k = len(clues)
    if k == 0:
        return 1
    slack = length - (sum(clues) + k - 1)
    if slack < 0:
        return float("inf")
    return comb(slack + k, k)
