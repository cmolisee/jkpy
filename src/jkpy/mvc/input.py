from __future__ import annotations

import sys
import termios
import tty
from typing import Any

from jkpy.utils import Ansi


class InputModel:
    """MVC Model for input interactions"""

    def __init__(self, prompt: str) -> None:
        self.prompt: str = prompt
        self.result: str | None = ""
        self.is_running: bool = True
        self._observers: list[Any] = []

    def add_observer(self, observer: Any) -> None:
        """Add observer to notify for updates. Observers must have update() function."""
        self._observers.append(observer)

    def notify_observers(self) -> None:
        """Notify all observers of an update"""
        for observer in self._observers:
            observer.update()

    def get_result(self) -> str | None:
        """returns the text response"""
        return self.result

    def stop(self) -> None:
        """stop the execution of this MVC"""
        self.is_running = False


class InputView:
    """MVC View for input interactions"""

    def __init__(self, model: InputModel) -> None:
        self.model: InputModel = model
        self.is_first_render: bool = True
        self.lines_to_overwrite: int = 0

    def clear(self) -> None:
        """Clear all lines set by lines_to_overwrite"""
        if self.lines_to_overwrite == 1:
            sys.stdout.write("\r")
            sys.stdout.write(Ansi.erase_line())
            sys.stdout.flush()
            return

        for _ in range(self.lines_to_overwrite):
            sys.stdout.write(Ansi.up(1))
            sys.stdout.write(Ansi.erase_line())
        sys.stdout.flush()

    def update(self) -> None:
        """Update the view."""
        self.render()

    def render(self) -> None:
        """Print the view to the terminal."""
        self.lines_to_overwrite = len(self.model.prompt.splitlines())

        if not self.is_first_render:
            self.clear()

        sys.stdout.write(self.model.prompt + " " + str(self.model.result))

        sys.stdout.flush()
        self.is_first_render = False

    def reset(self) -> None:
        """Resets first render which triggers the view to be cleared."""
        self.is_first_render = True


class InputController:
    """MVC Controller for input interactions"""

    def __init__(self, model: InputModel, view: InputView) -> None:
        self.model: InputModel = model
        self.view: InputView = view

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
        if key == "ENTER":
            self.model.stop()
        elif self.model.result and key == "BACKSPACE":
            self.model.result = self.model.result[:-1]
            self.view.update()
        elif (
            key
            and key.isalnum()
            or key
            in [
                ".",
                "\\",
                "/",
                "?",
                "-",
                "&",
                "%",
                ",",
                '"',
                "'",
                "_",
                "+",
                "=",
                "$",
                "[",
                "]",
                "(",
                ")",
                ":",
            ]
        ):
            if not self.model.result:
                self.model.result = key
            elif len(self.model.result) < 50:
                self.model.result += key
            self.view.update()

    def run(self) -> str | None:
        """Initiate the options mvc"""
        self.view.render()
        while self.model.is_running:
            key = self.get_key()
            self.handle_input(Ansi.from_code(key))

        print()
        return self.model.result


class Input:
    """Helper class with static methods for easily creating instances of the input MVC's"""

    @staticmethod
    def confirm(question: str) -> bool:
        """Create Input MVC for a confirmation prompt"""
        model: InputModel = InputModel(question + " (y/n)")
        view: InputView = InputView(model)
        controller: InputController = InputController(model, view)

        result = controller.run()
        print()

        if result and result.lower() in ("y", "yes"):
            return True

        return False

    @staticmethod
    def text(question: str) -> str | None:
        """Create Input MVC for a textual response prompt"""
        model: InputModel = InputModel(question)
        view: InputView = InputView(model)
        controller: InputController = InputController(model, view)

        return controller.run()
