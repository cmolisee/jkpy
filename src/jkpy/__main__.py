from datetime import date
import argparse
from jkpy.app_mvc import AppModel
from jkpy.app_mvc import AppView
from jkpy.app_mvc import AppController
from jkpy.services import run_application
from jkpy.services import show_configurations
from jkpy.services import edit_configurations
from jkpy.services import show_help
from jkpy.services import exit_application
from jkpy.utils import Print
from functools import partial

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
        "--remove-labels",
        nargs="*",
        help="Remove label(s) from configuration"
    )
    
    return parser.parse_args()

def main():
    options=[
        "Run Application",
        "View Configurations",
        "Edit Configurations",
        "Help",
        "Exit"
    ]
    
    model=AppModel(options)
    view=AppView(model)
    controller=AppController(model, view)
    
    model.add_observer(view)
    
    controller.register_handler(0, partial(run_application))
    controller.register_handler(1, partial(show_configurations))
    controller.register_handler(2, partial(edit_configurations))
    controller.register_handler(3, partial(show_help))
    controller.register_handler(4, partial(exit_application))
    
    # render only once
    print(f"{Print.MAGENTA}{view.banner()}{Print.NC}")
    
    try:
        controller.run()
    except KeyboardInterrupt:
        exit_application()
    
if __name__=="__main__":
    main()