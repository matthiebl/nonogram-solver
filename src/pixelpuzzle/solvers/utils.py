from pixelpuzzle.solvers import Square


def deduce_empty_line(length: int, clues: list[int]) -> str:
    if not clues:
        return Square.WHITE * length

    known_length = sum(clues) + len(clues) - 1
    gap = length - known_length

    print(clues, gap)

    if gap == 0:
        result = Square.BLACK * clues[0]
        for clue in clues[1:]:
            result += Square.WHITE + Square.BLACK * clue
        return result

    left = []
    for i, clue in enumerate(clues[:-1], start=1):
        left += [i] * clue + [0]
    left += [len(clues)] * clues[-1] + [0] * gap

    right = [0] * gap + [1] * clues[0]
    for i, clue in enumerate(clues[1:], start=2):
        right += [0] + [i] * clue

    return "".join(
        [Square.BLACK if a > 0 and a == b else Square.BLANK for a, b in zip(left, right)]
    )


def create_possibilities(clues: tuple[int], mask: str) -> tuple[str]:
    if not clues:
        if mask.count(Square.BLACK) > 0:
            return tuple()
        return (Square.WHITE * len(mask),)

    options = []

    (clue, *remaining_clues) = clues
    leave = sum(remaining_clues) + len(remaining_clues)
    for white in range(len(mask) - leave - clue + 1):
        prefix = Square.WHITE * white + Square.BLACK * clue
        if len(prefix) != len(mask):
            prefix += Square.WHITE
        if not all(m == p or m == Square.BLANK for m, p in zip(mask, prefix)):
            continue
        possibilities = create_possibilities(
            tuple(remaining_clues),
            mask[len(prefix) :],
        )
        if not possibilities:
            continue
        options += [prefix + p for p in possibilities]

    return tuple(option for option in options)


def increment_state(clues: tuple[int], state: str) -> str:
    possibilities = create_possibilities(clues, state)

    probabilities = {i: {Square.BLACK: 0, Square.WHITE: 0} for i in range(len(state))}
    for option in possibilities:
        for i, c in enumerate(option):
            probabilities[i][c] += 1

    return "".join(
        Square.BLACK
        if chance[Square.WHITE] == 0
        else Square.WHITE
        if chance[Square.BLACK] == 0
        else Square.BLANK
        for chance in probabilities.values()
    )
