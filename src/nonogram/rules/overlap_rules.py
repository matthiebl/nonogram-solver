from nonogram.core import Cell, Clues, LineState
from nonogram.exceptions import CellConflictContradiction, LineTooShortContradiction
from nonogram.rules import Rule
from nonogram.rules.simple_rules import black_runs


class OverlapRule(Rule):
    """The classic overlap/simple boxes technique. Finds cells that must be black in
    all valid clue placements by overlapping the earliest and latest possible positions."""

    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        if not clues or state.is_complete():
            return state

        earliest = earliest_starts(clues, state)
        latest = latest_starts(clues, state)

        new = LineState(state)

        for clue, early, late in zip(clues, earliest, latest):
            start = max(early, late)
            end = min(early + clue, late + clue)

            for i in range(start, end):
                if new[i] == Cell.CROSS:
                    raise CellConflictContradiction()
                new[i] = Cell.BOX

        return new


class NeverBlackRule(Rule):
    """Complement to OverlapRule. Marks any cell that cannot be black in any valid
    clue placement as a cross (outside the coverage range of all clues)."""

    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        if not clues or state.is_complete():
            return state

        earliest = earliest_starts(clues, state)
        latest = latest_starts(clues, state)

        coverage = [False] * len(state)

        for clue, early, late in zip(clues, earliest, latest):
            for i in range(early, late + clue):
                coverage[i] = True

        new = LineState(state)
        for i, can_be_black in enumerate(coverage):
            if not can_be_black:
                if state[i] == Cell.BOX:
                    raise CellConflictContradiction(
                        "Overlap suggests cell can never be black", clues, state
                    )
                new[i] = Cell.CROSS

        return new


class MinimumLengthExpansionRule(Rule):
    """For a black run bounded on one side, expands it to the minimum clue length
    that could own it. If only one clue can own it, places crosses at both endpoints."""

    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        n = len(state)
        new_state = LineState(state)

        if not clues or state.is_complete():
            return new_state

        earliest = earliest_starts(clues, state)
        latest = latest_starts(clues, state)

        runs = black_runs(state)

        for run_start, run_len in runs:
            left_bounded = run_start == 0 or state[run_start - 1] == Cell.CROSS
            right_end = run_start + run_len
            right_bounded = right_end == n or state[right_end] == Cell.CROSS

            if not (left_bounded or right_bounded) or (left_bounded and right_bounded):
                continue

            # Find candidate clue(s) that could cover this run
            possible_clues = set()
            for i, clue_len in enumerate(clues):
                s_earliest = earliest[i]
                s_latest = latest[i]
                if s_earliest <= run_start <= s_latest + clue_len - 1:
                    possible_clues.add(clues[i])

            if not possible_clues:
                continue

            required_length = min(clue for clue in possible_clues if clue >= run_len)
            start = run_start if left_bounded else run_start + run_len - required_length
            for i in range(start, start + required_length):
                if i >= n or new_state[i] == Cell.CROSS:
                    raise CellConflictContradiction()
                new_state[i] = Cell.BOX

            if len(possible_clues) == 1:
                if start - 1 >= 0:
                    new_state[start - 1] = Cell.CROSS
                if start + required_length < n:
                    new_state[start + required_length] = Cell.CROSS

        return new_state


class RunCappingRule(Rule):
    """Caps a black run with crosses when it has reached the maximum length any owning clue
    could have. The adjacent cells on both sides cannot be black, so they become crosses."""

    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        if not clues or state.is_complete():
            return state

        earliest = earliest_starts(clues, state)
        latest = latest_starts(clues, state)

        new = LineState(state)
        n = len(state)

        for run_start, run_len in black_runs(state):
            run_end = run_start + run_len

            possible_clues = [
                clues[i]
                for i in range(len(clues))
                if earliest[i] <= run_start
                and latest[i] + clues[i] >= run_end
                and clues[i] >= run_len
            ]

            if not possible_clues:
                continue

            if run_len == max(possible_clues):
                if run_start > 0:
                    if new[run_start - 1] == Cell.BOX:
                        raise CellConflictContradiction()
                    new[run_start - 1] = Cell.CROSS
                if run_end < n:
                    if new[run_end] == Cell.BOX:
                        raise CellConflictContradiction()
                    new[run_end] = Cell.CROSS

        return new


class ForcedSeparationRule(Rule):
    """When two BOX runs are separated by a single unknown that no clue can span across,
    that unknown must be a cross separating two distinct clues."""

    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        if not clues or state.is_complete():
            return state

        earliest = earliest_starts(clues, state)
        latest = latest_starts(clues, state)

        new = LineState(state)
        runs = black_runs(state)

        for (a_start, a_len), (b_start, b_len) in zip(runs, runs[1:]):
            gap_start = a_start + a_len
            if b_start - gap_start != 1 or state[gap_start] != Cell.UNKNOWN:
                continue

            b_end = b_start + b_len
            span_len = b_end - a_start

            can_span = any(
                clues[i] >= span_len and earliest[i] <= a_start and latest[i] + clues[i] >= b_end
                for i in range(len(clues))
            )

            if not can_span:
                new[gap_start] = Cell.CROSS

        return new


class UniqueAssignmentRule(Rule):
    """When a BOX run has only one possible owning clue, uses the run's position to
    tighten that clue's window and marks additional cells as black from the overlap.
    This is strictly stronger than OverlapRule for the uniquely-assigned clue."""

    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        if not clues or state.is_complete():
            return state

        earliest = earliest_starts(clues, state)
        latest = latest_starts(clues, state)

        new = LineState(state)

        for run_start, run_len in black_runs(state):
            run_end = run_start + run_len

            candidates = [
                i
                for i in range(len(clues))
                if earliest[i] <= run_start
                and latest[i] + clues[i] >= run_end
                and clues[i] >= run_len
            ]

            if len(candidates) != 1:
                continue

            c = candidates[0]
            clue_len = clues[c]

            # Tighten the window: clue must start early enough to cover run_end
            # and late enough to not start after run_start
            tight_earliest = max(earliest[c], run_end - clue_len)
            tight_latest = min(latest[c], run_start)

            for i in range(tight_latest, tight_earliest + clue_len):
                if new[i] == Cell.CROSS:
                    raise CellConflictContradiction()
                new[i] = Cell.BOX

        return new


class ClueOrderingConstraintRule(Rule):
    """When a BOX run is uniquely assigned to clue k, the adjacent clues are constrained
    by ordering: clue k-1 must end before the run, and clue k+1 must start after it.
    Tightening these windows can expose additional overlap cells for the neighbours."""

    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        if not clues or state.is_complete():
            return state

        earliest = earliest_starts(clues, state)
        latest = latest_starts(clues, state)

        new = LineState(state)
        n = len(state)

        for run_start, run_len in black_runs(state):
            run_end = run_start + run_len

            candidates = [
                i
                for i in range(len(clues))
                if earliest[i] <= run_start
                and latest[i] + clues[i] >= run_end
                and clues[i] >= run_len
            ]

            if len(candidates) != 1:
                continue

            k = candidates[0]

            # Clue k-1 must end at or before run_start - 2 (1-cell gap before run)
            # so it starts at or before run_start - clues[k-1] - 1
            if k > 0:
                tight_latest_prev = run_start - clues[k - 1] - 1
                if tight_latest_prev < earliest[k - 1]:
                    raise CellConflictContradiction()
                if tight_latest_prev < latest[k - 1]:
                    # Tighter window expands the overlap leftward
                    for i in range(tight_latest_prev, earliest[k - 1] + clues[k - 1]):
                        if new[i] == Cell.CROSS:
                            raise CellConflictContradiction()
                        new[i] = Cell.BOX

            # Clue k+1 must start at or after run_end + 1 (1-cell gap after run)
            if k < len(clues) - 1:
                tight_earliest_next = run_end + 1
                if tight_earliest_next > latest[k + 1]:
                    raise CellConflictContradiction()
                if tight_earliest_next > earliest[k + 1]:
                    # Tighter window expands the overlap rightward
                    for i in range(latest[k + 1], tight_earliest_next + clues[k + 1]):
                        if i >= n or new[i] == Cell.CROSS:
                            raise CellConflictContradiction()
                        new[i] = Cell.BOX

        return new


class LockedRunsRule(Rule):
    """When the number of black runs equals the number of clues, and every adjacent pair
    of runs cannot be connected — either because a cross already separates them, or because
    merging them would produce a run longer than the clue assigned to the left run — each
    run is uniquely locked to its clue. Any unknown cell outside the reachable extent of
    every run must be a cross.

    The reachable extent of run i (assigned clue c) extends at most c - current_length
    cells beyond the run in either direction, clipped to the run's segment (the region
    between the nearest confirmed crosses or line edges)."""

    @staticmethod
    def apply(clues: Clues, state: LineState) -> LineState:
        if not clues or state.is_complete():
            return state

        runs = black_runs(state)

        if len(runs) != len(clues):
            return state

        # Each adjacent pair must be impossible to connect: either a cross already
        # separates them, or the combined run would exceed the left run's clue.
        for i in range(len(runs) - 1):
            run_end = runs[i][0] + runs[i][1]
            next_start = runs[i + 1][0]
            gap = next_start - run_end
            combined = runs[i][1] + gap + runs[i + 1][1]
            has_cross = any(state[j] == Cell.CROSS for j in range(run_end, next_start))
            if not has_cross and (combined <= clues[i] or combined <= clues[i + 1]):
                return state

        n = len(state)
        reachable = [False] * n

        for idx, (run_start, run_length) in enumerate(runs):
            clue = clues[idx]
            run_end = run_start + run_length
            slack = clue - run_length

            seg_start = 0
            for j in range(run_start - 1, -1, -1):
                if state[j] == Cell.CROSS:
                    seg_start = j + 1
                    break

            seg_end = n
            for j in range(run_end, n):
                if state[j] == Cell.CROSS:
                    seg_end = j
                    break

            left_extent = max(seg_start, run_start - slack)
            right_extent = min(seg_end, run_end + slack)

            for j in range(left_extent, right_extent):
                reachable[j] = True

        new = LineState(state)
        for j in range(n):
            if state[j] == Cell.UNKNOWN and not reachable[j]:
                new[j] = Cell.CROSS

        return new


def earliest_starts(clues: Clues, state: LineState) -> list[int]:
    """Returns the indices of the earliest start to each clue.
    Ignores some aspects of current cells, other than completely impossible

    Raises:
        LineTooShortContradiction: When unable to find a place for all clues

    Returns:
        list[int]: A list of earliest indices for the left of each clue
    """

    starts = []
    pos = 0

    for clue in clues:
        while True:
            if pos + clue > len(state):
                raise LineTooShortContradiction()

            if (
                any(state[i] == Cell.CROSS for i in range(pos, pos + clue))
                or (pos > 0 and state[pos - 1] == Cell.BOX)
                or (pos + clue < len(state) and state[pos + clue] == Cell.BOX)
            ):
                pos += 1
                continue

            # Accept placement
            break

        starts.append(pos)
        pos += clue + 1

    return starts


def latest_starts(clues: Clues, state: LineState) -> list[int]:
    """Returns the indices of the latest start to each clue.
    Ignores some aspects of current cells, other than completely impossible

    Raises:
        LineTooShortContradiction: When unable to find a place for all clues

    Returns:
        list[int]: A list of latest indices for the left of each clue
    """
    n = len(state)

    # Reverse everything
    rev_state = LineState(state[::-1])
    rev_clues = Clues(clues[::-1])
    rev_starts = earliest_starts(rev_clues, rev_state)

    # Map reversed starts back to original indices
    return [n - (start + clue) for start, clue in zip(rev_starts, rev_clues)][::-1]
