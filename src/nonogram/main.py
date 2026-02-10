from nonogram.core import Grid, LineClue
from nonogram.printer import NonogramPrinter
from nonogram.rules.overlap_rules import NeverBlackRule, OverlapRule
from nonogram.solver.engine import PropagationEngine
from nonogram.solver.line_solver import LineSolver


def solve_nonogram():
    row_clues = [LineClue([2]), LineClue([1]), LineClue([1]), LineClue([1]), LineClue([1])]
    col_clues = [LineClue([5]), LineClue([1]), LineClue([]), LineClue([]), LineClue([])]
    grid = Grid(len(col_clues), len(row_clues))
    line_solver = LineSolver(rules=[OverlapRule(), NeverBlackRule()])
    engine = PropagationEngine(line_solver=line_solver)
    engine.propagate(grid, row_clues, col_clues)
    printer = NonogramPrinter(grid, row_clues, col_clues)
    print(printer)


solve_nonogram()
