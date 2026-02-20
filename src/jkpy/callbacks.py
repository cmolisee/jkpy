from __future__ import annotations
from typing import TYPE_CHECKING
from jkpy.handlers import Handlers
from jkpy.utils import Ansi
from jkpy.mvc.input import Input
from jkpy.mvc.select import Select
from functools import partial
import polars as pl

if TYPE_CHECKING:
    from jkpy.mvc.menu import MenuModel
    from jkpy.mvc.menu import MenuView
    from jkpy.mvc.menu import MenuController

def run_application(**kwargs) -> int:
    model: MenuModel = kwargs.get("model")
    view: MenuView = kwargs.get("view")
    
    try:
        handler_chain=Handlers.create_chain()
        
        view.clear()
        print(f"{Ansi.GREEN}{Ansi.BOLD}Running Application{Ansi.RESET}")
        print(Ansi.GREEN+view.line_break()+Ansi.RESET)
        
        handler_chain.handle(model, view)
        return 0
    except Exception:
        import traceback
        print(Ansi.RED+traceback.format_exc()+Ansi.RESET)
        return 1

def show_configurations(**kwargs) -> int:
    model: MenuModel = kwargs.get("model")
    view: MenuView = kwargs.get("view")
    
    try:
        view.clear()
        print("Configurations >"+ view.line_break()[len(15):])
        print(view.line_break())
        
        df=pl.json_normalize(model.get_data())
        df=df.with_columns(
            [
                # Use pl.format to wrap the joined string in brackets, like a Python list representation
                pl.format("[{}]", pl.col(pl.List).list.join(","))
            ]
        )
        print(Ansi.GREEN+df.transpose(include_header=True, header_name="key", column_names=["value"])+Ansi.RESET)
        
        print(view.line_break())
    except Exception:
        import traceback
        print(Ansi.RED+traceback.format_exc()+Ansi.RESET)
        model.stop()
    finally:
        return 0 if confirm("Do you wish to continue?") else model.stop()

def setter_prompt(**kwargs) -> int:
    model: MenuModel = kwargs.get("model")
    key: str = kwargs.get("key")
    
    if key in ["host", "path", "token"]:
        response=Input.text(f"Enter '{key}' value: ")
    elif key in ["members", "labels", "statuses", "teams", "ignore_labels"]:
        response=Input.text(f"Enter '{key}' value(s) separated by a comma ',': ")
        response=response.split(",") if not None else None
    else:
        selector=key.replace("remove_", "")
        response=Select.multiselect("Select values to remove:", model.get_data()[selector])
    
    if response is not None:
        model.set_data({ key: response})
    
    return 0

def back(**kwargs) -> int:
    model: MenuModel = kwargs.get("model")
    model.is_running=False
    return 0
        
def edit_configurations(**kwargs) -> int:
    view: MenuView = kwargs.get("view")
    options=[
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
        "Back"
    ]
    
    callbacks={
        0: partial(setter_prompt, "host"),
        1: partial(setter_prompt, "labels"),
        2: partial(setter_prompt, "members"),
        3: partial(setter_prompt, "path"),
        4: partial(setter_prompt, "statuses"),
        5: partial(setter_prompt, "teams"),
        6: partial(setter_prompt, "token"),
        7: partial(setter_prompt, "ignore_labels"),
        8: partial(setter_prompt, "remove_labels"),
        9: partial(setter_prompt, "remove_members"),
        10: partial(setter_prompt, "remove_statuses"),
        11: partial(setter_prompt, "remove_teams"),
        12: partial(setter_prompt, "remove_ignore_labels"),
        13: back
    }
    
    # clear and reset previous menu view
    view.clear()
    view.reset()
    
    # create new instance of app mvc
    sub_model=MenuModel(options)
    sub_view=MenuView(sub_model)
    sub_controller=MenuController(sub_model, sub_view)
    
    sub_model.add_observer(view)
    
    # register all callbacks
    for idx, callback in callbacks.items():
        sub_controller.register_callback(idx, callback)
    
    try:
        sub_controller.run()
    except KeyboardInterrupt:
        sub_model.is_running=False
    return 0

def exit_application(**kwargs) -> int:
    model: MenuModel = kwargs.get("model")
    model.stop()
    return 0
