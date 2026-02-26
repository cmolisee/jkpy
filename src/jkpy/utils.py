from datetime import date
from datetime import datetime
from typing import Any
from typing import Literal
import json
import termios
import tty
import sys
import re
import time
import asyncio

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o) -> str|Any:
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)
    
class Ansi:
    # https://talyian.github.io/ansicolors/
    RED="\x1b[31m"
    GREEN="\x1b[32m"
    YELLOW="\x1b[33m"
    CYAN="\x1b[36m"
    MAGENTA="\x1b[35m"
    
    BOLD="\x1b[1m"
    RESET="\x1b[0m"
    
    @staticmethod
    def up(y) -> str:
        """Move cursor up 'y' lines, to beginning of line"""
        return f"\x1b[{y}F"
    
    @staticmethod
    def right(x) -> str:
        """Move cursor right 'x' columns"""
        return f"\x1b[{x}C"
    
    @staticmethod
    def overwrite() -> str:
        """Overwrite all text from cursor, for the next n bits of output"""
        return "\x1b[K"
    
    @staticmethod
    def erase_line() -> str:
        """Erase the entire current line"""
        return f"\x1b[2K"
    
    @staticmethod
    def to_col(n) -> str:
        return f"\x1b[{n}G"
    
def get_cursor_position() -> (tuple[int, int] | tuple[Literal[-1], Literal[-1]]):
    """Reads cursor position (x, y) using ANSI codes."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    try:
        sys.stdout.write("\x1b[6n")
        sys.stdout.flush()
        buf = ""
        while not buf.endswith('R'):
            buf += msvcrt.getch().decode("utf-8") if sys.platform == "win32" else sys.stdin.read(1)
        matches = re.match(r".*\[(?P<y>\d*);(?P<x>\d*)R", buf)
        return (int(matches.group("x")), int(matches.group("y"))) if matches else (-1, -1)
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, old_settings)

class ProgressBar:
    def __init__(self, width, cursor):
        self.width=width
        self.cursor=cursor or 1
        self._progress=0.0
        self._start=None

    async def _animate(self):
        self._start=time.monotonic()
        while True:
            elapsed=time.monotonic()-self._start

            # asymptotic deceleration
            cap=1
            speed=1
            inner=1/(1+elapsed/speed) # from 1, decay to 0 
            invert=1-inner # invert decay from 0 to 1
            target=cap*invert # scale cap at 1.0

            self._progress=max(self._progress, target)
            self._render(self._progress)
            await asyncio.sleep(0.05)

    def _render(self, progress):
        filled=int(self.width * progress)
        bar="#"*filled+" "*(self.width-filled)
        sys.stdout.write(Ansi.to_col(self.cursor))
        sys.stdout.write(f"[{bar}] {progress * 100:5.1f}%")
        sys.stdout.flush()

    async def run_with(self, coro):
        """Run a coroutine while animating, then snap to 100%."""
        task=asyncio.create_task(self._animate())
        try:
            return await coro
        finally:
            task.cancel()
            self._render(1.0)
            sys.stdout.write("\n")
            sys.stdout.flush()


# def progress_bar(iteration, total, length, fill="#", empty=" ", cursor_start=0) -> None:
#     percent: str=("{0:0.1f}").format(100*(iteration/float(total)))
#     filled_length: int=int(length*iteration//total)
#     bar: str=fill*filled_length+empty*(length-filled_length)
    
#     sys.stdout.write(Ansi.to_col(cursor_start))
#     sys.stdout.write(f"{bar} {percent}%")
#     sys.stdout.flush()