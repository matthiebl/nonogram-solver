import pytest

from nonogram.core import Clues, LineState
from nonogram.rules.edge_rules import GlueEdgeRule, MercuryEdgeRule
from nonogram.rules.enumeration_rules import EnumerationRule
from nonogram.rules.overlap_rules import MinimumLengthExpansionRule, NeverBlackRule, OverlapRule
from nonogram.rules.simple_rules import CompleteCluesRule, FirstClueGapRule
from nonogram.rules.split_rules import CompleteEdgeSplitRule
from nonogram.solver.split_line_solver import SplitLineSolver
from tst.nonogram.utils import assert_state_at_least


class TestLineSolverCompleteness:
    line_solver = SplitLineSolver(
        rules=[
            CompleteCluesRule(),
            OverlapRule(),
            GlueEdgeRule(),
            MercuryEdgeRule(),
            FirstClueGapRule(),
            MinimumLengthExpansionRule(),
            NeverBlackRule(),
            CompleteCluesRule(),
        ],
        split_rules=[
            CompleteEdgeSplitRule(),
        ],
    )

    @pytest.mark.parametrize(
        "clues, state",
        [
            ((), ""),
            ((2, 2, 2, 2, 5), "   .#  .#  .# ..##.   .#####.."),
            # ((5, 1, 8, 1), "                     #   #   ."),
        ],
    )
    def test_completeness(self, clues, state):
        """
        Ideally, our line solver that makes use of all the defined rules in the correct order
        should be at least as good as the enumeration rule, with a much lower complexity of
        calculation.
        """
        clues = Clues(clues)

        assert assert_state_at_least(
            self.line_solver.solve(clues, LineState(state)),
            EnumerationRule.apply(clues, LineState(state)),
        )
