from __future__ import annotations

import sys
from datetime import datetime
from functools import partial
from typing import Any

import polars as pl

from jkpy.handlers import Handlers
from jkpy.mvc.input import Input
from jkpy.mvc.menu import MenuController, MenuModel, MenuView
from jkpy.mvc.options import Options
from jkpy.utils import Ansi


def run_application(**kwargs: Any) -> None:
    """Callback to run the primary handler chain of this program."""
    try:
        model: MenuModel = kwargs["model"]
        view: MenuView = kwargs["view"]
        handler_chain = Handlers.create_chain()

        print()

        handler_chain.handle(model, view)
        sys.exit(0)
    except Exception:
        import traceback

        print(Ansi.RED + traceback.format_exc() + Ansi.RESET)
        sys.exit(1)


def show_configurations(**kwargs: Any) -> None:
    """Callback to print the application configurations to the terminal"""
    try:
        model: MenuModel = kwargs["model"]

        print()

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
        cfg = model.get_configs()
        # extract relevant items
        config = {k: cfg[k] for k in keys if k in cfg}
        # clean the values
        for k, v in config.items():
            if isinstance(v, datetime):
                config[k] = v.strftime("%Y-%m-%d")
            elif isinstance(v, list):
                config[k] = "[]" if not v else ",".join(v)
            elif v is None:
                config[k] = ""
            else:
                config[k] = str(v)

        df = pl.json_normalize(config, strict=False)
        print(
            Ansi.GREEN
            + df.transpose(include_header=True, header_name="key", column_names=["value"])
            + Ansi.RESET
        )

        if not Input.confirm("Do you wish to continue?"):
            model.stop()

        return
    except Exception:
        import traceback

        print(Ansi.RED + traceback.format_exc() + Ansi.RESET)
        sys.exit(1)


def setter_prompt(**kwargs: Any) -> None:
    """Callback to prompt the user for setting a specific configuration"""
    try:
        model: MenuModel = kwargs["model"]
        key: str = kwargs["key"]

        response: Any = None
        if key in ["host", "path", "token"]:
            response = Input.text(f"Enter '{key}' value: ")
        elif key in ["members", "labels", "statuses", "teams", "ignore_labels"]:
            response = Input.text(f"Enter '{key}' value(s) separated by a comma ',': ")
            response = response.split(",") if response else None
        elif key in [
            "remove_labels",
            "remove_members",
            "remove_statuses",
            "remove_teams",
            "remove_ignore_labels",
        ]:
            key = key.replace("remove_", "")
            response = Options.multiselect("Select values to remove:", model.get_configs()[key])

        if response is not None:
            model.set_configs({key: response})

        return None
    except Exception:
        import traceback

        print(Ansi.RED + traceback.format_exc() + Ansi.RESET)
        sys.exit(1)


def back(**kwargs: Any) -> None:
    """Callback to return from the current submenu"""
    try:
        model: MenuModel = kwargs["model"]
        model.is_running = False
        return None
    except Exception:
        import traceback

        print(Ansi.RED + traceback.format_exc() + Ansi.RESET)
        sys.exit(1)


def edit_configurations(**kwargs: Any) -> None:
    """Callback to navigate to the configuration submenu."""
    try:
        options: list[str] = [
            "Set Host",
            "Set Labels",
            "Set Members",
            "Set Output Path",
            "Set Statuses",
            "Set Teams",
            "Set Token",
            "Set Ignore Labels",
            "Remove Labels",
            "Remove Members",
            "Remove Statuses",
            "Remove Teams",
            "Remove Ignore Labels",
            "Back",
        ]

        callbacks: dict[int, Any] = {
            0: partial(setter_prompt, key="host"),
            1: partial(setter_prompt, key="labels"),
            2: partial(setter_prompt, key="members"),
            3: partial(setter_prompt, key="path"),
            4: partial(setter_prompt, key="statuses"),
            5: partial(setter_prompt, key="teams"),
            6: partial(setter_prompt, key="token"),
            7: partial(setter_prompt, key="ignore_labels"),
            8: partial(setter_prompt, key="remove_labels"),
            9: partial(setter_prompt, key="remove_members"),
            10: partial(setter_prompt, key="remove_statuses"),
            11: partial(setter_prompt, key="remove_teams"),
            12: partial(setter_prompt, key="remove_ignore_labels"),
            13: back,
        }

        # create new instance of app mvc
        sub_model = MenuModel(options)
        sub_view = MenuView(sub_model)
        sub_controller = MenuController(sub_model, sub_view)

        sub_model.add_observer(sub_view)

        # register all callbacks
        for idx, callback in callbacks.items():
            sub_controller.register_callback(idx, callback)

        sub_controller.run()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        import traceback

        print(Ansi.RED + traceback.format_exc() + Ansi.RESET)
        sys.exit(1)
    return None


def exit_application(**kwargs: Any) -> None:
    """Callback to stop application execution and exit the application"""
    try:
        model: MenuModel = kwargs["model"]
        model.stop()
        return None
    except Exception:
        import traceback

        print(Ansi.RED + traceback.format_exc() + Ansi.RESET)
        sys.exit(1)
