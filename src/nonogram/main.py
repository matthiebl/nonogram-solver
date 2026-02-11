from nonogram.parser import parse_nonogram
from nonogram.printer import NonogramPrinter
from nonogram.rules.edge_rules import EdgeWorkerRule
from nonogram.rules.overlap_rules import NeverBlackRule, OverlapRule
from nonogram.rules.simple_rules import CompleteCluesRule
from nonogram.solver.engine import PropagationEngine
from nonogram.solver.line_solver import LineSolver


def solve_nonogram(path: str):
    puzzle = parse_nonogram(path)
    line_solver = LineSolver(
        rules=[CompleteCluesRule(), EdgeWorkerRule(), OverlapRule(), NeverBlackRule()]
    )
    engine = PropagationEngine(line_solver=line_solver)

    engine.propagate(puzzle.grid, puzzle.row_clues, puzzle.col_clues)

    printer = NonogramPrinter(puzzle.grid, puzzle.row_clues, puzzle.col_clues)
    print(printer)


solve_nonogram("examples/flat_out.json")
