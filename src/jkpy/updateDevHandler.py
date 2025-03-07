"""jkpy updateDevHandler"""
# jkpy/updateDevHandler.py

from jkpy.jiraHandler import JiraHandler
from jkpy.utils import sys_exit
from requests.auth import HTTPBasicAuth
import pandas as pd
import click
import requests
import json


class UpdateDevHandler(JiraHandler):
    """UpdateDevHandler(JiraHandler)
    
    Concrete implementation of the JiraHandler interface.
    Responsible for finding tickets with multiple name labels and no developer label, 
    prompting user, and updating the ticket.
    """

    def handle(self, request):
        """UpdateDevHandler(JiraHandler).hanlde(self, request)
        
        Concrete implementation of the handle() method from JiraHandler.
        Filter all tickets from all datasets.
        Identify tickets with multiple name labels and no developer.
        Prompt user for the primary developer and update the ticket in Jira.
        """

        request.log("UpdateDevHandler().handle().")
        if not request.proceed:
            sys_exit(0, request, "request.proceed is False. Exiting.")
        
        if not request.token:
            sys_exit(1, request, "Could not find jira api token required for authentication.")
        
        if not request.email:
            sys_exit(1, request, "Could not find jira email required for authentication.")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

        for i, responseData in enumerate(request.responseList):
            df=pd.json_normalize(responseData.get("issues", []))

            for j, row in df.iterrows():
                # if a primary developer is already set, skip
                if not pd.isna(row.get("fields.customfield_10264.displayName", pd.NA)):
                    continue;
                
                labels=row['fields.labels']
                labelSet=set(labels)
                nameSet=set(request.nameLabels)
                intersection=labelSet.intersection(nameSet)

                if len(intersection) > 1:
                    message=f"Select a primary developer for issue {row["key"]} : "
                    options=sorted(list(filter(lambda x: x in request.accountIds, intersection)))
                    selection=self.prompt_and_select(options, message) if len(options) > 1 else options[0]
                    # update the ticket in jira and in this run
                    self.send_update_request(request, selection, row['key'])
                    request.responseList[i]["issues"][j]["fields"]["customfield_10264"]=request.accountIds[selection]
        
        return super().handle(request)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    def prompt_and_select(self, options, prompt_message="Select an option"):
        """Prompts the user to select an option from a list. """

        click.echo(prompt_message)
        for i, option in enumerate(options):
            click.echo(f"{i + 1}. {option}")

        while True:
            try:
                selection = int(click.prompt("Enter the number of your selection"))
                if 1 <= selection <= len(options):
                    return options[selection - 1]
                else:
                    click.echo("Invalid selection. Please try again.")
            except ValueError:
                click.echo("Invalid input. Please enter a number.")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    def send_update_request(self, request, labelName, ticketId):
        """Make Jira request to update the developer field."""
        print(request.accountIds[labelName]["accountId"])
        try:
            displayName=labelName.replace("-", " ")
            response=requests.request(
                method="PUT",
                url=f"https://creditonebank.atlassian.net/rest/api/3/issue/{ticketId}",
                headers={ "Accept": "application/json", "Content-Type": "application/json" },
                auth=HTTPBasicAuth(request.email, request.token),
                data=json.dumps({
                    "update": {
                        "customfield_10264": [{ "set": { "id": request.accountIds[labelName]["accountId"] }}]
                    }
                }),
                verify=False
            )
            
            if response.status_code != 204 and response.status_code != 200:
                sys_exit(1, request, f"request failed: \n {response.status_code}, {response.reason}, {response.text}")

            request.log(f"Success updating {displayName} as primary developer on ticket: {ticketId}")
        except Exception as e:
            sys_exit(1, request, f"exception occured processing request: {e}")