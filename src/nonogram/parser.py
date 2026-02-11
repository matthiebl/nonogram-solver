"""
Parser for custom JSON format

{
    "version": "1",
    "meta": {
        "title": <str>,
        "author": <str>,
        "difficulty": <int>, # 1 - 5 default supported emoji
    },
    "width": <int>,
    "height: <int>,
    "rows": <list[list[int]]>, # left to right
    "cols": <list[list[int]]>, # top to bottom
    "grid": <list[str] | None>
}
"""

import json
from dataclasses import dataclass
from typing import Any

from nonogram.core import Grid, LineClue, LineView


class ParseError(Exception):
    pass


@dataclass
class PuzzleInput:
    meta: dict[str, Any]
    width: int
    height: int
    row_clues: list[LineClue]
    col_clues: list[LineClue]
    grid: Grid


def parse_nonogram(path: str) -> PuzzleInput:
    with open(path) as f:
        data = json.load(f)

    try:
        width = int(data["width"])
        height = int(data["height"])
        row_clues = [LineClue(row) for row in data["rows"]]
        col_clues = [LineClue(col) for col in data["cols"]]

        grid = Grid(width, height)
        if "grid" in data:
            if len(data["grid"]) != height:
                raise ParseError("Provided grid height does not match height")
            if any(len(row) != width for row in data["grid"]):
                raise ParseError("Provided grid width does not match width")
            for i, row in enumerate(data["grid"]):
                grid.apply_row(i, LineView(row))

    except KeyError as e:
        raise ParseError(f"Missing required field: {e}")

    if len(row_clues) != height:
        raise ParseError("Row count does not match height")
    if len(col_clues) != width:
        raise ParseError("Column count does not match width")

    row_clue_sum = sum(sum(row) for row in row_clues)
    col_clue_sum = sum(sum(col) for col in col_clues)
    if row_clue_sum != col_clue_sum:
        raise ParseError(
            f"Row and column clues sum to different totals, {row_clue_sum} != {col_clue_sum}"
        )

    return PuzzleInput(
        meta=data["meta"] if "meta" in data else {},
        width=width,
        height=height,
        row_clues=row_clues,
        col_clues=col_clues,
        grid=grid,
    )
