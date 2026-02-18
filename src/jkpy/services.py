from __future__ import annotations
from typing import Any
import json
from jkpy.handlers import Handlers
from jkpy.utils import DateTimeEncoder
from jkpy.utils import Print
from jkpy.prompt_mvc import confirm
from jkpy.app_mvc import show_submenu
from jkpy.prompt_mvc import text_input
from jkpy.prompt_mvc import multiselect
from functools import partial

def run_application(model: 'AppModel', view: 'AppView') -> int:
    try:
        handler_chain=Handlers.create_chain()
        Print.green("Running Application")
        Print.green(view.line_break())
        handler_chain.handle(model, view)
        return 0
    except Exception:
        import traceback
        Print.red(traceback.format_exc())
        return 1

def show_configurations(model: 'AppModel', view: 'AppView') -> int:
    is_continue=False
    try:
        print()
        Print.green(f"Configurations")
        Print.green(view.line_break())
        Print.green(json.dumps(model.get_data(), cls=DateTimeEncoder, indent=2))
        is_continue=confirm("Do you wish to continue?")
    except Exception:
        import traceback
        Print.red(traceback.format_exc())
    finally:
        if is_continue:
            print()
            return 0
        else:
            model.stop()

def setter_prompt(key: str, model: 'AppModel', view: 'AppView'):
    if key in ["host", "path", "token"]:
        val=text_input(f"Enter '{key}' value: ")
    elif key in ["members", "labels", "statuses", "teams"]:
        val=text_input(f"Enter '{key}' value(s) separated by a comma ',': ")
        val=val.split(",") if not None else None
    else:
        selector=key.replace("remove_", "")
        val=multiselect("Select values to remove:", model.get_data()[selector])
        
    if val is not None:
        model.set_data({ key: val})
    
def edit_configurations(model: 'AppModel', view: 'AppView') -> int:
    show_submenu([
        "Set Host",
        "Set Labels",
        "Set Members",
        "Set Output Path",
        "Set Statuses",
        "Set Teams",
        "Set Token",
        "Remove Labels",
        "Remove Members",
        "Remove Statuses",
        "Remove Teams",
    ], {
        0: partial(setter_prompt, "host"),
        1: partial(setter_prompt, "labels"),
        2: partial(setter_prompt, "members"),
        3: partial(setter_prompt, "path"),
        4: partial(setter_prompt, "statuses"),
        5: partial(setter_prompt, "teams"),
        6: partial(setter_prompt, "token"),
        7: partial(setter_prompt, "remove_labels"),
        8: partial(setter_prompt, "remove_members"),
        9: partial(setter_prompt, "remove_statuses"),
        10: partial(setter_prompt, "remove_teams"),
    })
    return 0

def show_help(model: 'AppModel', view: 'AppView') -> int:
    Print.red("TODO: implement show_help\n")
    return 0

def exit_application(model: 'AppModel', view: 'AppView') -> int:
    Print.green("Goodbye...\n")
    model.stop()
