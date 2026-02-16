from nonogram.core import LineClue, LineView


class Rule:
    cost = "MEDIUM"

    @staticmethod
    def apply(clues: LineClue, state: LineView) -> LineView:
        """Apply a rule that updates a line.

        Args:
            clues (LineClue): List of clues valid over the state.
            state (LineView): Line state to apply the rule to.

        Returns:
            LineView: The (potentially) updated line state.
        """
        raise NotImplementedError()


class SplitRule:
    @staticmethod
    def apply(clues: LineClue, state: LineView) -> tuple[tuple[LineClue, LineView]]:
        """Apply a splitting rule that strips clues and resolved

        Args:
            clues (LineClue): List of clues valid over the state.
            state (LineView): Line state to apply the rule to.

        Returns:
            list[tuple[LineClue, LineView]]: A list of clue and state pairs.
        """
        raise NotImplementedError()
