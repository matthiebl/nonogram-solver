from nonogram.core import CellState, LineClue, LineView
from nonogram.exceptions import CellConflictContradiction
from nonogram.rules import Rule
from nonogram.rules.utils import earliest_starts, latest_starts


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
