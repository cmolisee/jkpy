from __future__ import annotations
from datetime import date
import argparse
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
from urllib3.exceptions import InsecureRequestWarning
import polars as pl
import urllib3

# disable warning for InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

pl.Config.set_fmt_str_lengths(1000)             # Character limit for string columns
pl.Config.set_tbl_cols(-1)                      # -1 shows all columns
pl.Config.set_tbl_rows(-1)                      # -1 shows all rows
pl.Config(tbl_formatting="UTF8_FULL")           # border on all row/column
# pl.Config.set_tbl_hide_column_names(True)       # hide header row name
# pl.Config.set_tbl_hide_column_data_types(True)  # hide header row data type

def parse_args():
    parser=argparse.ArgumentParser(
        prog="jkpy",
        description="TUI to build metrics from JIRA.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--config",
        action="store_true",
        help="Return configs as JSON string",
    )
    
    parser.add_argument(
        "--email",
        help="Jira email configuration"
    )

    parser.add_argument(
        "--token",
        help="Jira API token configuration"
    )

    parser.add_argument(
        "--path",
        help="Output Path configuration"
    )

    parser.add_argument(
        "--members",
        nargs="*",
        default=None,
        help="Target members configuration"
    )

    parser.add_argument(
        "--teams",
        nargs="*",
        help="Target teams configuration"
    )

    parser.add_argument(
        "--statuses",
        nargs="*",
        help="Target Statuses configuration"
    )

    parser.add_argument(
        "--labels",
        nargs="*",
        help="Target labels configuration"
    )
    
    parser.add_argument(
        "--ignore-labels",
        nargs="*",
        help="Target labels to ignore configuration"
    )

    parser.add_argument(
        "--start",
        default=date(date.today().year, 1, 1).isoformat(),
        help="Target start date configuration. Defaults to start of year"
    )

    parser.add_argument(
        "--end",
        default=date.today().strftime("%Y-%m-%d"),
        help="Target end date configuration. Defaults to today"
    )
    
    parser.add_argument(
        "--host",
        help="Host for Jira API calls"
    )
    
    parser.add_argument(
        "--remove-members",
        nargs="*",
        help="Remove member(s) from configuration"
    )

    parser.add_argument(
        "--remove-teams",
        nargs="*",
        help="Remove team(s) from configuration"
    )

    parser.add_argument(
        "--remove-statuses",
        nargs="*",
        help="Remove status(es) from configuration"
    )
    
    parser.add_argument(
        "--remove-ignore-labels",
        nargs="*",
        help="Remove to ignore labels configuration"
    )

    parser.add_argument(
        "--remove-labels",
        nargs="*",
        help="Remove label(s) from configuration"
    )
    
    return parser.parse_args()

def main() -> None:
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