from nonogram.core import LineState


class EngineObserver:
    def on_solved(self) -> None:
        pass

    def on_step(self, kind: str, index: int) -> None:
        pass

    def on_line_update(self, kind: str, index: int, old: LineState, new: LineState) -> None:
        pass
