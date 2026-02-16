from argparse import ArgumentParser

from rich.console import Console
from rich.live import Live

from nonogram.parser import parse_nonogram
from nonogram.printer import RichObserver
from nonogram.rules.edge_rules import GlueEdgeRule, MercuryEdgeRule
from nonogram.rules.overlap_rules import NeverBlackRule, OverlapRule
from nonogram.rules.simple_rules import CompleteCluesRule
from nonogram.solver.engine import PropagationEngine
from nonogram.solver.line_solver import LineSolver


def solve_nonogram(path: str) -> None:
    puzzle = parse_nonogram(path)
    rules = [
        CompleteCluesRule(),
        GlueEdgeRule(),
        MercuryEdgeRule(),
        OverlapRule(),
        NeverBlackRule(),
    ]
    line_solver = LineSolver(rules=rules)

    Console()
    with Live(None, refresh_per_second=10) as live:
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
