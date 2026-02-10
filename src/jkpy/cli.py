import argparse
from typing import Optional
from datetime import date
import sys
import json
from jkpy.configuration import Configuration
from jkpy.handlers import Handlers
from jkpy.utils import DateTimeEncoder

def create_parser() -> argparse.ArgumentParser:
    parser=argparse.ArgumentParser(
        prog="jkpy",
        description="TUI to build metrics from JIRA.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
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
    
    return parser

def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    parser=create_parser()
    return parser.parse_args(args)

def main() -> None:
    args=parse_args()
    
    try:
        if args.config:
            config=Configuration.get_config()
            print(json.dumps(config, DateTimeEncoder))
            return 0
        
        args_dict=vars(args)
        request={**args_dict}
        
        handler_chain=Handlers.create_chain()
        request=Configuration.set_config(request)
        
        handler_chain.handle(request)
    except KeyboardInterrupt:
        print("\nOperation cancelled by usre", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
        
if __name__=="__main__":
    sys.exit(main())

# from . import __app_name__
# from jkpy.configHandler import ConfigHandler
# from jkpy.jiraRequest import JiraRequest
# from jkpy.jqlSetupHandler import JqlSetupHandler
# from jkpy.metricHandler import MetricHandler
# from jkpy.requestHandler import RequestHandler
# from jkpy.resultsHandler import ResultsHandler
# from jkpy.typer_types import *
# from jkpy.updateDevHandler import UpdateDevHandler
# from jkpy.userMappingHandler import UserMappingHandler
# from typing_extensions import Annotated
# import typer

# app=typer.Typer(
#     name=__app_name__,
#     help="Process Jira data and create reports",
#     add_completion=False,
# )

# @app.callback(invoke_without_command=True)
# def main(
#     email: Annotated[str, emailOption]=None,
#     token: Annotated[str, tokenOption]=None,
#     isSetup: Annotated[bool, isSetupOption]=False,
#     folderPath: Annotated[str, folderPathOption]=None,
#     teamLabels: Annotated[str, teamLabelsOption]=None,
#     nameLabels: Annotated[str, nameLabelsOption]=None,
#     statusTypes: Annotated[str, statusTypesOption]=None,
#     metricLabels: Annotated[str, metricLabelsOption ]=None,
#     remove_metricLabels: Annotated[str, remove_metricLabelsOption]=None,
#     remove_statusTypes: Annotated[str, remove_statusTypesOption]=None,
#     remove_teamLabels: Annotated[str, remove_teamLabelsOption ]=None,
#     remove_nameLabels: Annotated[str, remove_nameLabelsOption]=None,
#     startDate: Annotated[str, startDateOption ]=None,
#     endDate: Annotated[str, endDateOption ]=None,
#     showConfig: Annotated[bool, showConfigOption]=False,
# ) -> None:
#     """Main application"""
    
#     request=JiraRequest({
#         "isSetup": isSetup,
#         "email": email,
#         "token": token,
#         "folderPath": folderPath,
#         "teamLabels": teamLabels,
#         "nameLabels": nameLabels,
#         "statusTypes": statusTypes,
#         "metricLabels": metricLabels,
#         "remove_teamLabels": remove_teamLabels,
#         "remove_nameLabels": remove_nameLabels,
#         "remove_statusTypes": remove_statusTypes,
#         "remove_metricLabels": remove_metricLabels,
#         "startDate": startDate,
#         "endDate": endDate,
#         "showConfig": showConfig
#     });
#     request.log("Initializing JiraRequest object...")
    
#     try:
#         # handler call chain
#         resultsHandler=ResultsHandler()
#         metricHandler=MetricHandler(resultsHandler)
#         updateDevHandler=UpdateDevHandler(metricHandler)
#         requestHandler=RequestHandler(updateDevHandler)
#         jqlSetupHandler=JqlSetupHandler(requestHandler)
#         userMappingHandler=UserMappingHandler(jqlSetupHandler)
#         configHandler=ConfigHandler(userMappingHandler)

#         configHandler.handle(request)

#         print("Complete. See output directory for log and report files.")
#     except Exception as e:
#         request.log(e);
    
# if __name__ == "__main__":
#     app()