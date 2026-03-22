from argparse import ArgumentParser

from rich.console import Console
from rich.live import Live

from nonogram.parser import parse_nonogram
from nonogram.printer import RichObserver
from nonogram.rules.edge_rules import GlueEdgeRule, MercuryEdgeRule
from nonogram.rules.overlap_rules import (
    ClueOrderingConstraintRule,
    ForcedSeparationRule,
    LockedRunsRule,
    MinimumLengthExpansionRule,
    NeverBlackRule,
    OverlapRule,
    RunCappingRule,
    UniqueAssignmentRule,
)
from nonogram.rules.simple_rules import CompleteCluesRule, FirstClueGapRule, GapTooSmallRule
from nonogram.rules.split_rules import CompleteEdgeSplitRule
from nonogram.solver.engine import PropagationEngine
from nonogram.solver.split_line_solver import SplitLineSolver


def make_line_solver() -> SplitLineSolver:
    """Build the standard rule pipeline used by both terminal and UI solvers."""
    return SplitLineSolver(
        rules=[
            CompleteCluesRule(),
            OverlapRule(),
            GlueEdgeRule(),
            MercuryEdgeRule(),
            FirstClueGapRule(),
            MinimumLengthExpansionRule(),
            RunCappingRule(),
            ForcedSeparationRule(),
            UniqueAssignmentRule(),
            ClueOrderingConstraintRule(),
            NeverBlackRule(),
            GapTooSmallRule(),
            LockedRunsRule(),
            CompleteCluesRule(),
        ],
        split_rules=[
            CompleteEdgeSplitRule(),
        ],
    )


def solve_nonogram(path: str) -> None:
    puzzle = parse_nonogram(path)

    line_solver = make_line_solver()

    Console()
    with Live(None, refresh_per_second=10) as live:
        observer = RichObserver(puzzle, live)
        engine = PropagationEngine(line_solver=line_solver, observer=observer)
        engine.propagate(puzzle.grid, puzzle.row_clues, puzzle.col_clues)


def open_ui(input_path: str | None = None) -> None:
    from nonogram.ui import NonogramApp

    NonogramApp(input_path=input_path).run()


def main() -> None:
    parser = ArgumentParser(prog="nonogram", description="Nonogram puzzle solver")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    solve_parser = subparsers.add_parser("solve", help="Solve a nonogram puzzle")
    solve_parser.add_argument("input", type=str, help="Input to solve")

    ui_parser = subparsers.add_parser("ui", help="Open interactive UI solver")
    ui_parser.add_argument(
        "--input", type=str, default=None, help="Optional puzzle JSON to load directly"
    )

    args = parser.parse_args()

    if args.command == "solve":
        solve_nonogram(args.input)
    elif args.command == "ui":
        open_ui(getattr(args, "input", None))


if __name__ == "__main__":
    main()
