from nonogram.core import LineClue, LineView
from nonogram.rules import Rule, SplitRule
from nonogram.solver.line_solver import LineSolver


class SplitLineSolver(LineSolver):
    def __init__(self, rules: list[Rule], split_rules: list[SplitRule]):
        super().__init__(rules)
        self.split_rules = split_rules

    def solve(self, clues: LineClue, state: LineView):
        curr = super().solve(clues, state)

        if curr.is_complete():
            return curr

        for rule in self.split_rules:
            rule = rule.new()
            segments = rule.split(clues, curr)
            if len(segments) == 1:
                continue

            states = []
            for segment_clues, segment_state in segments:
                states.append(self.solve(segment_clues, segment_state))

            curr = rule.merge(tuple(states))

        return curr
