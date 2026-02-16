from nonogram.core import CellState, LineClue, LineView
from nonogram.exceptions import CellConflictContradiction
from nonogram.rules import Rule


def mirror_rule(rule):
    def mirrored(clues: LineClue, state: LineView):
        new = rule(LineClue(clues[::-1]), LineView(state[::-1]))
        return LineView(new[::-1])

    return mirrored


class EdgeRule(Rule):
    @classmethod
    def apply(cls, clues: LineClue, state: LineView) -> LineView:
        left = cls.apply_left_to_right(clues, state)
        return mirror_rule(cls.apply_left_to_right)(clues, left)

    @staticmethod
    def apply_left_to_right(clues: LineClue, state: LineView) -> LineView:
        raise NotImplementedError()


class CompleteEdgeRule(EdgeRule):
    @staticmethod
    def apply_left_to_right(clues: LineClue, state: LineView) -> LineView:
        if state.is_complete():
            return state
        if not clues:
            if any(cell == CellState.BLACK for cell in state):
                raise CellConflictContradiction("No clues remaining require non-black state")
            return LineView([CellState.WHITE] * len(state))

        i = 0
        while i < len(state) and state[i] == CellState.WHITE:
            i += 1
        if i == len(state) or state[i] == CellState.UNKNOWN:
            return state

        # Here we have worked up to a left touching black, which must be the first clue
        clue = clues[0]
        for j in range(i, i + clue):
            if state[j] == CellState.WHITE:
                raise CellConflictContradiction()
            state[j] = CellState.BLACK

        if j + 1 == len(state):
            return state

        if state[j + 1] == CellState.BLACK:
            raise CellConflictContradiction()
        state[j + 1] = CellState.WHITE

        return LineView(
            state[: j + 1]
            + CompleteEdgeRule.apply_left_to_right(LineClue(clues[1:]), LineView(state[j + 1 :]))
        )


class GlueEdgeRule(EdgeRule):
    @staticmethod
    def apply_left_to_right(clues: LineClue, state: LineView) -> LineView:
        if state.is_complete():
            return state
        if not clues:
            if any(cell == CellState.BLACK for cell in state):
                raise CellConflictContradiction("No clues remaining require non-black state")
            return LineView([CellState.WHITE] * len(state))

        i = 0
        while i < len(state) and state[i] == CellState.WHITE:
            i += 1

        clue = clues[0]
        black = 0
        for _ in range(i, i + clue):
            if black:
                if state[i] == CellState.WHITE:
                    raise CellConflictContradiction()
                state[i] = CellState.BLACK
            if state[i] == CellState.BLACK:
                black += 1
            i += 1

        if i >= len(state):
            return state

        if black == clue:
            if state[i] == CellState.BLACK:
                raise CellConflictContradiction()
        elif state[i] in (CellState.BLACK, CellState.UNKNOWN) or not black:
            return state

        state[i] = CellState.WHITE
        return LineView(
            state[:i] + GlueEdgeRule.apply_left_to_right(LineClue(clues[1:]), LineView(state[i:]))
        )


class MercuryEdgeRule(EdgeRule):
    @staticmethod
    def apply_left_to_right(clues: LineClue, state: LineView) -> LineView:
        if state.is_complete():
            return state
        if not clues:
            if any(cell == CellState.BLACK for cell in state):
                raise CellConflictContradiction("No clues remaining require non-black state")
            return LineView([CellState.WHITE] * len(state))

        i = 0
        while i < len(state) and state[i] == CellState.UNKNOWN:
            i += 1

        clue = clues[0]
        if i > clue:
            return state

        empty = i
        while i < len(state) and state[i] == CellState.BLACK:
            i += 1

        black = i - empty
        if black == 0:
            return state

        for k in range(empty + black - clue):
            state[k] = CellState.WHITE

        if state[i] == CellState.WHITE:
            for k in range(i - clue, i - 1):
                state[k] = CellState.BLACK

        return state
