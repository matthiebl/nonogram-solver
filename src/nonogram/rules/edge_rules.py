from nonogram.core import CellState, LineClue, LineView
from nonogram.exceptions import CellConflictContradiction
from nonogram.rules import Rule


class EdgeWorkerRule(Rule):
    @staticmethod
    def apply(clues: LineClue, state: LineView) -> LineView:
        updated = EdgeWorkerRule.apply_left_to_right(clues, state)

        reverse = LineView(updated[::-1])
        reverse_clues = LineClue(clues[::-1])

        updated = EdgeWorkerRule.apply_left_to_right(reverse_clues, reverse)
        return LineView(updated[::-1])

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
            + EdgeWorkerRule.apply_left_to_right(LineClue(clues[1:]), LineView(state[j + 1 :]))
        )
