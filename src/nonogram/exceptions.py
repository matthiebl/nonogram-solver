class NonogramError(Exception):
    pass


class Contradiction(NonogramError):  # noqa: N818
    pass


class CellConflictContradiction(Contradiction):
    pass


class LineTooShortContradiction(Contradiction):
    pass
