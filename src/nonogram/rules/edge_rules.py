from collections.abc import Callable

from nonogram.core import Cell, Clues, LineState
from nonogram.exceptions import CellConflictContradiction
from nonogram.rules import Rule


def mirror_rule(
    rule: Callable[[Clues, LineState], LineState],
) -> Callable[[Clues, LineState], LineState]:
    def mirrored(clues: Clues, state: LineState) -> LineState:
        new = rule(Clues(clues[::-1]), LineState(state[::-1]))
        return LineState(new[::-1])

    return mirrored


class EdgeRule(Rule):
    @classmethod
    def apply(cls, clues: Clues, state: LineState) -> LineState:
        left = cls.apply_left_to_right(clues, state)
        return mirror_rule(cls.apply_left_to_right)(clues, left)

    @staticmethod
    def apply_left_to_right(clues: Clues, state: LineState) -> LineState:
        raise NotImplementedError()


class CompleteEdgeRule(EdgeRule):
    """Recursively processes from the edge inward. When a black run touches the edge,
    commits it if it matches the first clue, marks gaps as crosses, and recurses."""

    @staticmethod
    def apply_left_to_right(clues: Clues, state: LineState) -> LineState:
        if state.is_complete():
            return state
        if not clues:
            if any(cell == Cell.BOX for cell in state):
                raise CellConflictContradiction("No clues remaining require non-black state")
            return LineState([Cell.CROSS] * len(state))

        i = 0
        while i < len(state) and state[i] == Cell.CROSS:
            i += 1
        if i == len(state) or state[i] == Cell.UNKNOWN:
            return state

        # Here we have worked up to a left touching black, which must be the first clue
        clue = clues[0]
        for j in range(i, i + clue):
            if state[j] == Cell.CROSS:
                raise CellConflictContradiction()
            state[j] = Cell.BOX

        if j + 1 == len(state):
            return state

        if state[j + 1] == Cell.BOX:
            raise CellConflictContradiction()
        state[j + 1] = Cell.CROSS

        return LineState(
            state[: j + 1]
            + CompleteEdgeRule.apply_left_to_right(Clues(clues[1:]), LineState(state[j + 1 :]))
        )


class GlueEdgeRule(EdgeRule):
    """More aggressive than CompleteEdgeRule. Forces partial black runs near the edge
    to complete to the first clue length, then separates with a cross and recurses."""

    @staticmethod
    def apply_left_to_right(clues: Clues, state: LineState) -> LineState:
        if state.is_complete():
            return state
        if not clues:
            if any(cell == Cell.BOX for cell in state):
                raise CellConflictContradiction("No clues remaining require non-black state")
            return LineState([Cell.CROSS] * len(state))

        i = 0
        while i < len(state) and state[i] == Cell.CROSS:
            i += 1

        clue = clues[0]
        black = 0
        for _ in range(i, i + clue):
            if black:
                if state[i] == Cell.CROSS:
                    raise CellConflictContradiction()
                state[i] = Cell.BOX
            if state[i] == Cell.BOX:
                black += 1
            i += 1

        if i >= len(state):
            return state

        if black == clue:
            if state[i] == Cell.BOX:
                raise CellConflictContradiction()
        elif state[i] in (Cell.BOX, Cell.UNKNOWN) or not black:
            return state

        state[i] = Cell.CROSS
        return LineState(
            state[:i] + GlueEdgeRule.apply_left_to_right(Clues(clues[1:]), LineState(state[i:]))
        )


class MercuryEdgeRule(EdgeRule):
    """Handles unknowns at the edge followed by a black run. If the gap is too small
    for the first clue, crosses it out. If the run is bounded by a cross, fills backward."""

    @staticmethod
    def apply_left_to_right(clues: Clues, state: LineState) -> LineState:
        if state.is_complete():
            return state
        if not clues:
            if any(cell == Cell.BOX for cell in state):
                raise CellConflictContradiction("No clues remaining require non-black state")
            return LineState([Cell.CROSS] * len(state))

        i = 0
        while i < len(state) and state[i] == Cell.UNKNOWN:
            i += 1

        clue = clues[0]
        if i > clue:
            return state

        empty = i
        while i < len(state) and state[i] == Cell.BOX:
            i += 1

        black = i - empty
        if black == 0:
            return state

        for k in range(empty + black - clue):
            state[k] = Cell.CROSS

        if state[i] == Cell.CROSS:
            for k in range(i - clue, i - 1):
                state[k] = Cell.BOX

        return state
