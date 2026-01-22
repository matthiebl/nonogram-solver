from argparse import ArgumentParser
from collections.abc import Callable
from enum import StrEnum

from pixelpuzzle.solvers.basic_solver import BasicSolver
from pixelpuzzle.solvers.utils import deduce_empty_line, increment_state
from pixelpuzzle.utils import InputParser


class CliCommand(StrEnum):
    SOLVE = "solve"
    REPL = "repl"


class Solvers(StrEnum):
    BASIC = "basic"


class ReplParser(StrEnum):
    ECHO = "echo"
    LINE = "line"
    INCR = "incr"


class ProcessType(StrEnum):
    SOLVER = "solver"


def main() -> None:
    parser = ArgumentParser(prog="pixel", description="Pixel Puzzle solver toolkit")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Solve command
    solve_parser = subparsers.add_parser(CliCommand.SOLVE, help="Solve a pixel puzzle")
    solve_parser.add_argument(
        "--input", "-i", type=str, required=True, help="Input to solve (.pix.json)"
    )
    solve_parser.add_argument(
        "--solver", "-s", type=Solvers, default=Solvers.BASIC, help="Solver type"
    )

    # Repl command
    repl_parser = subparsers.add_parser(CliCommand.REPL, help="Interactive REPL")
    repl_parser.add_argument("--input", "-i", type=str, help="Input to parse")
    repl_parser.add_argument(
        "--parser",
        type=ReplParser,
        choices=list(ReplParser),
        required=True,
        help="The parser to run",
    )

    args = parser.parse_args()

    if args.command == CliCommand.SOLVE:
        solve_puzzle(args.input, args.solver)
    elif args.command == CliCommand.REPL:
        if args.parser == ReplParser.ECHO:
            base_repl(echo_repl)
        elif args.parser == ReplParser.LINE:
            base_repl(line_repl)
        elif args.parser == ReplParser.INCR:
            base_repl(incr_repl)
        else:
            raise ValueError(f"Repl parser `{args.parser}` is not valid")
    else:
        raise ValueError("Invalid command found!")


def solve_puzzle(file_path: str, solver_type: Solvers) -> None:
    puzzle_input = InputParser.parse(file_path)

    if solver_type == Solvers.BASIC:
        solver = BasicSolver.of(puzzle_input)
    else:
        raise ValueError(f"Solver type `{solver_type}` is not valid")

    print(solver)

    while True:
        try:
            response = input("Step (ENTER) | Save (s <file>) | Quit (q) > ")
        except ValueError:
            continue
        except EOFError:
            break
        except KeyboardInterrupt:
            break

        if response.lower() == "q":
            return
        if response[0].lower() == "s":
            try:
                filename = response.split()[1]
                with open(filename, "w") as file:
                    file.write(InputParser.to_text(solver))
                print(f"Saved current state to {filename}\n")
            except IndexError:
                print("No file name provided!\n")
            except Exception as e:
                print("Failed to write to output:", type(e).__name__, e, "\n")
        elif solver.iterate():
            print("Complete!")
            return


def base_repl(f: Callable[[str], None]) -> None:
    while True:
        try:
            f(input("> "))
        except ValueError:
            continue
        except EOFError:
            break
        except KeyboardInterrupt:
            break


def echo_repl(line: str) -> None:
    print(line)


def line_repl(line: str) -> None:
    [length, *clues] = list(map(int, line.split()))
    res = deduce_empty_line(length, clues)
    print("|" + "|".join(list(res)) + "|")


def incr_repl(line: str) -> None:
    [state, nums] = line.split("|")
    clues = list(map(int, nums.split()))
    length = len(state)
    left_over = length + 1 - sum(clues) - len(clues)

    complexity = 1
    for c in clues:
        complexity *= max(1, left_over - c + 1)
    if complexity > 90000000000:
        print("-", display_state(state), clues, "!!!")
        return

    res = increment_state(tuple(clues), state)

    if res != state:
        print("!", end=" ", flush=True)
    else:
        print(" ", end=" ", flush=True)
    print(display_state(res), clues)


def display_state(state: str) -> str:
    return "|" + "|".join([state[i : i + 5] for i in range(0, len(state), 5)]) + "|"


if __name__ == "__main__":
    main()
