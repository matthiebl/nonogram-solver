from nonogram.core import Clues, LineState
from nonogram.rules import Rule, SplitRule
from nonogram.solver.line_solver import LineSolver


class SplitLineSolver(LineSolver):
    def __init__(self, rules: list[Rule], split_rules: list[SplitRule]):
        super().__init__(rules)
        self.split_rules = split_rules

    def solve(self, clues: Clues, state: LineState) -> LineState:
        curr = super().solve(clues, state)

        if curr.is_complete():
            return curr

        for split_rule in self.split_rules:
            split_rule = split_rule.new()
            segments = split_rule.split(clues, curr)
            if len(segments) == 1:
                continue

            states = []
            for segment_clues, segment_state in segments:
                if segment_clues == clues and segment_state == state:
                    states.append(segment_state)
                else:
                    states.append(self.solve(segment_clues, segment_state))

            curr = split_rule.merge(tuple(states))

        return curr
