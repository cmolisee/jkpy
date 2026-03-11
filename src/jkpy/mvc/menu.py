from __future__ import annotations

import json
import os
import shutil
import sys
import termios
import tty
from datetime import date, datetime
from pathlib import Path
from typing import Any

from jkpy.utils import Ansi, DateTimeEncoder


class MenuModel:
    """MVC Model for Menu interactions"""

    def __init__(self, options: list[str]) -> None:
        self.config_path: Path = Path(os.path.join(Path.home(), "Documents/.jkpy/config.txt"))

        # setup configurations
        self.data: dict[str, Any] = self.get_configs()
        self.data["start"] = date(date.today().year, 1, 1).isoformat()
        self.data["end"] = date.today().strftime("%Y-%m-%d")
        self.data["data_frames"] = {}

        if isinstance(self.data["start"], str):
            self.data["start"] = datetime.fromisoformat(self.data["start"]).replace(tzinfo=None)

        if isinstance(self.data["end"], str):
            self.data["end"] = datetime.fromisoformat(self.data["end"]).replace(tzinfo=None)

        # mvc variables
        self.options: list[str] = options
        self.selected: int = 0
        self.is_running: bool = True
        self._observers: list[Any] = []

    def get_configs(self) -> Any:
        """Get configs from local cache"""
        try:
            with open(self.config_path) as f:
                data: str = f.read()
                return json.loads(data)
        except FileNotFoundError:
            print(
                Ansi.YELLOW
                + ">>> Configuration file does not exist. Returning runtime configs.\n"
                + Ansi.RESET
            )
            return self.data

    def set_configs(self, config: dict[str, Any]) -> dict[str, Any]:
        """Set configs in local cache"""
        keys = [
            "email",
            "token",
            "path",
            "members",
            "teams",
            "statuses",
            "labels",
            "ignore_labels",
            "host",
            "start",
            "end",
        ]
        # make directory if DNE
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_path, "w") as f:
                for key, value in config.items():
                    if key == "path":
                        Path(value).mkdir(parents=True, exist_ok=True)
                        self.data[key] = value
                    elif key in [
                        "remove_members",
                        "remove_teams",
                        "remove_statuses",
                        "remove_labels",
                        "remove_ignore_labels",
                    ]:
                        data_key = key.replace("remove_", "")
                        data_list = self.data[data_key]

                        updated_list = [item for item in data_list if item not in value]
                        self.data[data_key] = sorted(updated_list)
                    elif key in self.data.keys():
                        self.data[key] = value
                    else:
                        continue  # skip non-conforming keys

                out = {k: self.data[k] for k in keys if k in self.data}
                json.dump(out, f, cls=DateTimeEncoder)
        except Exception:
            pass

        return self.data

    def add_observer(self, observer: Any) -> None:
        """Add observer to notify for updates. Observers must have update() function."""
        self._observers.append(observer)

    def notify_observers(self) -> None:
        """Notify all observers of an update"""
        for observer in self._observers:
            observer.update()

    def select_previous(self) -> None:
        """Update selected option to previous selection. notify observers."""
        self.selected = (self.selected - 1) % len(self.options)
        self.notify_observers()

    def select_next(self) -> None:
        """Update selected option to next selection. notify observers."""
        self.selected = (self.selected + 1) % len(self.options)
        self.notify_observers()

    def stop(self) -> None:
        """stop the execution of this MVC"""
        self.is_running = False


class MenuView:
    """MVC View for menu interactions"""

    PLUS = r"""+"""
    BAR = r"""|"""
    DASH = r"""-"""
    BANNER_LARGE = [
        r"""     _   _  __  ____   __   __""",
        r"""    | | | |/ / |  _ \  \ \ / /""",
        r""" _  | | | ' /  | |_) |  \ V / """,
        r"""| |_| | | . \  |  __/    | |  """,
        r""" \___/  |_|\_\ |_|       |_|  """,
    ]
    BANNER_SMALL = [
        r"""     _   _  __ """,
        r"""    | | | |/ / """,
        r""" _  | | | ' /  """,
        r"""| |_| | | . \  """,
        r""" \___/  |_|\_\ """,
        r""" ____   __   __""",
        r"""|  _ \  \ \ / /""",
        r"""| |_) |  \ V / """,
        r"""|  __/    | |  """,
        r"""|_|       |_|  """,
    ]
    BANNER_SUBTITLE = """Tool for Generating KPI's in Jira"""

    def __init__(self, model: MenuModel) -> None:
        self.model: MenuModel = model
        self.is_first_render: bool = True
        self.lines_to_overwrite: int = 0

    def _width(self) -> int:
        """Gets width in columns of the terminal view"""
        try:
            return round(shutil.get_terminal_size().columns * (2 / 3))
        except OSError:  # Fallback
            return 64

    def line_break(self) -> str:
        """Renders a formatted line break"""
        return self.DASH * self._width()

    def banner(self) -> str:
        """Renders banner"""
        width: int = self._width()
        horizontal_border: str = self.PLUS + self.DASH * (width - 2) + self.PLUS
        empty_line: str = self.BAR + (" " * (width - 2) + self.BAR)

        if width < 20:  # tiny size
            return self.BANNER_SUBTITLE
        elif width < 40:  # small size
            banner = self.BANNER_SMALL
        else:  # regular size
            banner = self.BANNER_LARGE

        banner_parts: list[str] = []
        banner_parts.append(horizontal_border)
        banner_parts.append(empty_line)

        for ln in banner:
            banner_parts.append(self.BAR + " " + ln + (" " * (width - 3 - len(ln))) + self.BAR)

        if width > 40:  # add subtitle if regular size
            banner_parts.append(
                self.BAR
                + " "
                + self.BANNER_SUBTITLE
                + " "
                + (" " * (width - 4 - len(self.BANNER_SUBTITLE)))
                + self.BAR
            )

        banner_parts.append(empty_line)
        banner_parts.append(horizontal_border)
        return "\n".join(banner_parts)

    def instructions(self) -> str:
        """Renders instructions"""
        return "Use UP/DOWN arrows to navigate, 'enter' to select, 'CTRL+C' to quit"

    def clear(self) -> None:
        """Clear all lines set by lines_to_overwrite"""
        for _ in range(self.lines_to_overwrite):
            sys.stdout.write(Ansi.up(1))
            sys.stdout.write(Ansi.erase_line())
        sys.stdout.flush()

    def update(self) -> None:
        """Update the view."""
        self.render()

    def render(self) -> None:
        """Print the view to the terminal."""
        instructions: str = f"{Ansi.YELLOW}{self.instructions()}{Ansi.RESET}"
        self.lines_to_overwrite = len(self.model.options) + len(instructions.splitlines())

        if not self.is_first_render:
            self.clear()

        sys.stdout.write(self.instructions() + "\n")
        for idx, opt in enumerate(self.model.options):
            if idx == self.model.selected:
                sys.stdout.write(f">{Ansi.CYAN}{opt}{Ansi.RESET}<\n")
            else:
                sys.stdout.write(f" {Ansi.CYAN}{opt}{Ansi.RESET}\n")

        sys.stdout.flush()
        self.is_first_render = False

    def reset(self) -> None:
        """Resets first render which triggers the view to be cleared."""
        self.is_first_render = True


class MenuController:
    """MVC Controller for options interactions"""

    def __init__(self, model: MenuModel, view: MenuView) -> None:
        self.model: MenuModel = model
        self.view: MenuView = view
        self.callbacks: dict[int, Any] = {}

    def register_callback(self, index: int, callback: Any) -> None:
        """Registers a callback function for a specific menu option"""
        self.callbacks[index] = callback

    def execute_selected(self) -> None:
        """Invokes selected menu option callback"""
        # get the selected callback
        callback = self.callbacks.get(self.model.selected)

        # clear lines and execute the callback
        if callback:
            self.view.clear()
            callback(model=self.model, view=self.view)

        # re-render the view after callback finishes
        if self.model.is_running:
            self.view.reset()
            self.view.render()

    def get_key(self) -> str | Any:
        """Retrieve keyboard input from terminal"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)

            if ch == "\x1b":
                # switch to timed non-blocking read mode
                # return immediately if data available or up to 0.1s before empty
                new_settings = termios.tcgetattr(fd)
                new_settings[6][termios.VMIN] = 0
                new_settings[6][termios.VTIME] = 1
                termios.tcsetattr(fd, termios.TCSANOW, new_settings)

                next_ch = sys.stdin.read(1)

                if next_ch == "[":
                    ch += next_ch

                    while True:
                        c = sys.stdin.read(1)
                        if not c:
                            break
                        ch += c
                        if c.isalpha() or c == "~":
                            break
                elif next_ch == "0":
                    # SS3 sequence (F1-F4)
                    ch += sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def handle_input(self, key: str | None) -> None:
        """Determine how to handle keyboard input received from terminal."""
        if key == "UP":
            self.model.select_previous()
        elif key == "DOWN":
            self.model.select_next()
        elif key == "ENTER":
            self.execute_selected()

    def run(self) -> None:
        """Initiate the options mvc"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            self.view.render()
            while self.model.is_running:
                key = self.get_key()
                self.handle_input(Ansi.from_code(key))
        except KeyboardInterrupt:
            sys.exit(0)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
