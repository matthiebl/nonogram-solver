from argparse import ArgumentParser

from rich.console import Console
from rich.live import Live

from nonogram.parser import parse_nonogram
from nonogram.printer import RichObserver, render_grid
from nonogram.rules.edge_rules import EdgeWorkerRule
from nonogram.rules.enumeration_rules import EnumerationRule
from nonogram.rules.overlap_rules import NeverBlackRule, OverlapRule
from nonogram.rules.simple_rules import CompleteCluesRule
from nonogram.solver.engine import PropagationEngine
from nonogram.solver.line_solver import LineSolver


def solve_nonogram(path: str):
    puzzle = parse_nonogram(path)
    line_solver = LineSolver(
        rules=[
            CompleteCluesRule(),
            EdgeWorkerRule(),
            OverlapRule(),
            NeverBlackRule(),
            EnumerationRule(),
        ]
    )

    console = Console()
    with Live(render_grid(puzzle.grid), refresh_per_second=5) as live:
        observer = RichObserver(puzzle, live)
        engine = PropagationEngine(line_solver=line_solver, observer=observer)
        engine.propagate(puzzle.grid, puzzle.row_clues, puzzle.col_clues)


def main() -> None:
    parser = ArgumentParser(prog="nonogram", description="Nonogram puzzle solver")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    solve_parser = subparsers.add_parser("solve", help="Solve a nonogram puzzle")
    solve_parser.add_argument("input", type=str, help="Input to solve")

    args = parser.parse_args()

    if args.command == "solve":
        solve_nonogram(args.input)


if __name__ == "__main__":
    main()
