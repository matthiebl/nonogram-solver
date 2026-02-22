# Nonogram Solver

A Python package for solving [nonogram](https://en.wikipedia.org/wiki/Nonogram) (picross, pixel puzzle) grids. It uses constraint propagation with a configurable set of line-solving rules to fill cells row-by-row and column-by-column until the puzzle is solved.

## Requirements

- Python 3.12+

## Installation

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

The `[dev]` extra adds pytest, ruff, mypy, and Rich for testing, linting, and live console output.

## Usage

### Command line

Solve a puzzle from a JSON file:

```bash
nonogram solve examples/small.json
```

The solver prints the grid to the console with live updates as it progresses. Black cells appear as filled blocks (██), white as empty (░░), and unknown as blank.

### Puzzle format

Puzzles use a custom JSON schema:

```json
{
  "version": "1",
  "meta": {
    "title": "Puzzle Name",
    "author": "Optional",
    "difficulty": 1
  },
  "width": 5,
  "height": 5,
  "rows": [[5], [1], [0], [0], [0]],
  "cols": [[1], [2], [1], [1], [1]],
  "grid": null
}
```

- **rows** – Row clues, left to right. Each row is a list of run lengths (e.g. `[3, 2]` = three black, gap, two black).
- **cols** – Column clues, top to bottom. Same format as rows.
- **grid** – Optional. Partial solution as an array of strings: `"#"` = black, `"."` = white, `" "` = unknown.

Example puzzles are in the `examples/` directory (`small.json`, `curious.json`, etc.).

## Architecture

The solver is built around:

- **`PropagationEngine`** – Iterates over rows and columns, applying the line solver whenever a line changes. Uses a work queue so that updated lines trigger re-processing of intersecting columns/rows.
- **`SplitLineSolver`** – For each line, applies a sequence of rules until no changes occur. When a line can be split into independent segments (e.g. by fully solved edge blocks), it solves each segment recursively and merges the results.
- **Rules** – Pure functions that take clues and a line state and return an updated line. Rules may raise some `Contradiction` when the puzzle is in an incorrect state.

### Included rules

| Rule | Description |
|------|-------------|
| TBC | TBC

## Development

```bash
# Run tests
pytest

# Lint
ruff check .

# Type check
mypy src/
```

## License

See the project license file.
