from __future__ import annotations
from typing import List
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView
from jkpy.mvc.menu import MenuController
from jkpy.callbacks import run_application
from jkpy.callbacks import show_configurations
from jkpy.callbacks import edit_configurations
from jkpy.callbacks import exit_application
from jkpy.utils import Ansi
from functools import partial
import polars as pl

pl.Config.set_fmt_str_lengths(1000)             # Character limit for string columns
pl.Config.set_tbl_cols(-1)                      # -1 shows all columns
pl.Config.set_tbl_rows(-1)                      # -1 shows all rows
pl.Config(tbl_formatting="UTF8_FULL")           # border on all row/column
# pl.Config.set_tbl_hide_column_names(True)       # hide header row name
# pl.Config.set_tbl_hide_column_data_types(True)  # hide header row data type

def main() -> None:
    """Main function of the application"""
    options: List[str]=[
        "Run Application",
        "View Configurations",
        "Edit Configurations",
        "Exit"
    ]
    
    model: MenuModel=MenuModel(options)
    view: MenuView=MenuView(model)
    controller: MenuController=MenuController(model, view)
    
    model.add_observer(view)
    
    controller.register_callback(0, partial(run_application))
    controller.register_callback(1, partial(show_configurations))
    controller.register_callback(2, partial(edit_configurations))
    controller.register_callback(3, partial(exit_application))
    
    # render only once
    print(f"{Ansi.MAGENTA}{view.banner()}{Ansi.RESET}")
    
    try:
        controller.run()
    except KeyboardInterrupt:
        exit_application(model=model)
    
if __name__=="__main__":
    main()