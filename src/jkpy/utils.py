import asyncio
import json
import sys
import time
from datetime import date, datetime
from typing import Any


class DateTimeEncoder(json.JSONEncoder):
    """Custom json encoder for handling date and datetime instances."""

    def default(self, o: object) -> str | Any:
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        return super().default(o)


class Ansi:
    """Utility class to assist with ansi codes, colors, and escape sequences."""

    # https://talyian.github.io/ansicolors/
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    CYAN = "\x1b[36m"
    MAGENTA = "\x1b[35m"

    BOLD = "\x1b[1m"
    RESET = "\x1b[0m"

    KEYS = {
        " ": "SPACE",
        "\r": "ENTER",
        "\n": "ENTER",
        "\x7f": "BACKSPACE",
        "\x1b": "ESCAPE",
        "\x1b[A": "UP",
        "\x1b[B": "DOWN",
        "\x1b[C": "RIGHT",
        "\x1b[D": "LEFT",
        "\x1b[1;2A": "SHIFT+UP",
        "\x1b[5~": "PAGE_UP",
        "\x1b[6~": "PAGE_DOWN",
        "\x1b[H": "HOME",
        "\x1b[F": "END",
        "\x1bOP": "F1",
        "\x1bOQ": "F2",
    }

    @staticmethod
    def from_code(k: str) -> str | None:
        """Get the string representation of the hexidecimal escape sequence or the key itself."""
        return Ansi.KEYS.get(k) if k in Ansi.KEYS.keys() else k

    @staticmethod
    def up(y: int) -> str:
        """Move cursor up 'y' lines, to beginning of line"""
        return f"\x1b[{y}F"

    @staticmethod
    def right(x: int) -> str:
        """Move cursor right 'x' columns"""
        return f"\x1b[{x}C"

    @staticmethod
    def overwrite() -> str:
        """Overwrite all text from cursor, for the next n bits of output"""
        return "\x1b[K"

    @staticmethod
    def erase_line() -> str:
        """Erase the entire current line"""
        return "\x1b[2K"

    @staticmethod
    def to_col(n: int) -> str:
        """Move cursor to column n"""
        return f"\x1b[{n}G"


class ProgressBar:
    """
    Utitily class to disaplay a progress bar for an asynchronous coroutine.
    """

    def __init__(self, width: int, cursor: int | None):
        self.width: int = width
        self.cursor: int = cursor or 1
        self._progress: float = 0.0
        self._start: float | None = None

    async def _animate(self) -> None:
        """Animation loop that calculates state using asymptotic deceleration."""
        self._start = time.monotonic()
        while True:
            elapsed = time.monotonic() - self._start

            # asymptotic deceleration parts
            cap = 1
            speed = 1
            inner = 1 / (1 + elapsed / speed)  # from 1, decay to 0
            invert = 1 - inner  # invert decay from 0 to 1
            target = cap * invert  # scale cap at 1.0

            self._progress = max(self._progress, target)
            self._render(self._progress)
            await asyncio.sleep(0.05)

    def _render(self, progress: float) -> None:
        """Render the current state."""
        filled = int(self.width * progress)
        bar = "#" * filled + " " * (self.width - filled)
        sys.stdout.write(Ansi.to_col(self.cursor))
        sys.stdout.write(f"[{bar}] {progress * 100:5.1f}%")
        sys.stdout.flush()

    async def run_with(self, coro: Any) -> Any:
        """Run a coroutine while animating, then snap to 100%."""
        task = asyncio.create_task(self._animate())
        try:
            return await coro
        finally:
            task.cancel()
            self._render(1.0)
            sys.stdout.write("\n")
            sys.stdout.flush()
