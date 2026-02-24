from nonogram.core import Clues, LineState


class Rule:
    cost = "MEDIUM"

    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        """Apply a rule that updates a line.

        Args:
            clues (LineClue): List of clues valid over the state.
            state (LineView): Line state to apply the rule to.

        Returns:
            LineView: The (potentially) updated line state.
        """
        raise NotImplementedError()


class SplitRule:
    def split(self, clues: Clues, state: LineState) -> tuple[tuple[Clues, LineState], ...]:
        """Apply a splitting rule that reduces the state into segments

        Args:
            clues (LineClue): List of clues valid over the state.
            state (LineView): Line state to apply the rule to.

        Returns:
            tuple[tuple[LineClue, LineView], ...]: A list of sub clue and state pairs.
        """
        raise NotImplementedError()

    def merge(self, segments: tuple[LineState, ...]) -> LineState:
        """Merge the segments of state this rule broke up

        Args:
            segments (tuple[LineView, ...]): List of state for the split segments.

        Returns:
            LineView: The merged state.
        """
        raise NotImplementedError()

    @classmethod
    def new(cls) -> "SplitRule":
        return cls()
