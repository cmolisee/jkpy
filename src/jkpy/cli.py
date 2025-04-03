from . import __app_name__
from jkpy.configHandler import ConfigHandler
from jkpy.jiraRequest import JiraRequest
from jkpy.jqlSetupHandler import JqlSetupHandler
from jkpy.metricHandler import MetricHandler
from jkpy.requestHandler import RequestHandler
from jkpy.resultsHandler import ResultsHandler
from jkpy.typer_types import *
from jkpy.updateDevHandler import UpdateDevHandler
from jkpy.userMappingHandler import UserMappingHandler
from typing_extensions import Annotated
import typer

app=typer.Typer(
    name=__app_name__,
    help="Process Jira data and create reports",
    add_completion=False,
)

@app.callback(invoke_without_command=True)
def main(
    email: Annotated[str, emailOption]=None,
    token: Annotated[str, tokenOption]=None,
    isSetup: Annotated[bool, isSetupOption]=False,
    folderPath: Annotated[str, folderPathOption]=None,
    teamLabels: Annotated[str, teamLabelsOption]=None,
    nameLabels: Annotated[str, nameLabelsOption]=None,
    statusTypes: Annotated[str, statusTypesOption]=None,
    metricLabels: Annotated[str, metricLabelsOption ]=None,
    remove_metricLabels: Annotated[str, remove_metricLabelsOption]=None,
    remove_statusTypes: Annotated[str, remove_statusTypesOption]=None,
    remove_teamLabels: Annotated[str, remove_teamLabelsOption ]=None,
    remove_nameLabels: Annotated[str, remove_nameLabelsOption]=None,
    startDate: Annotated[str, startDateOption ]=None,
    endDate: Annotated[str, endDateOption ]=None,
    showConfig: Annotated[bool, showConfigOption]=False,
) -> None:
    """Main application"""
    
    request=JiraRequest({
        "isSetup": isSetup,
        "email": email,
        "token": token,
        "folderPath": folderPath,
        "teamLabels": teamLabels,
        "nameLabels": nameLabels,
        "statusTypes": statusTypes,
        "metricLabels": metricLabels,
        "remove_teamLabels": remove_teamLabels,
        "remove_nameLabels": remove_nameLabels,
        "remove_statusTypes": remove_statusTypes,
        "remove_metricLabels": remove_metricLabels,
        "startDate": startDate,
        "endDate": endDate,
        "showConfig": showConfig
    });
    request.log("Initializing JiraRequest object...")
    
    # handler call chain
    resultsHandler=ResultsHandler()
    metricHandler=MetricHandler(resultsHandler)
    updateDevHandler=UpdateDevHandler(metricHandler)
    requestHandler=RequestHandler(updateDevHandler)
    jqlSetupHandler=JqlSetupHandler(requestHandler)
    userMappingHandler=UserMappingHandler(jqlSetupHandler)
    configHandler=ConfigHandler(userMappingHandler)

    configHandler.handle(request)

    print("Complete. See output directory for log and report files.")
    
if __name__ == "__main__":
    app()