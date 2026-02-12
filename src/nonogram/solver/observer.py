from nonogram.core import LineView


class EngineObserver:
    def on_solved(self) -> None:
        pass

    def on_step(self, kind: str, index: int) -> None:
        pass

    def on_line_update(self, kind: str, index: int, old: LineView, new: LineView) -> None:
        pass
