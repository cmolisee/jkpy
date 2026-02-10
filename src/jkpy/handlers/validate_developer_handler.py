from typing import Any
from typing import List
from typing import Tuple
from jkpy.handlers.base_handler import BaseHandler
from jkpy.configuration import ConfigurationType
from jkpy.configuration import Configuration
from jkpy.prompt import Prompt
import json
import polars as pl
import requests
from requests.auth import HTTPBasicAuth
from jkpy.utils import DateTimeEncoder

class ValidateDeveloperHandler(BaseHandler):
    def handle(self, request: ConfigurationType) -> None:
        missing_developer=request["original_data"].select(pl.col("fields.customfield_10264.displayName").is_null)
        for row in missing_developer.iter_rows():
            issue_key=row["key"]
            options=self.get_developer_options(request, row)
            message=f"Issue {issue_key} is missing the primary developer field. Choose which member to assign as the primary developer:"
            
            chosen_option=self.prompt(request, message, options)
            
            self.jira_update(request, chosen_option, issue_key)
            request["original_data"].with_columns(
                pl.when(pl.col("id") == 3)
                .then(pl.lit(99))
                .otherwise(pl.col("value"))
                .alias("value")
            )
            
    def get_developer_options(self, request: ConfigurationType, row: tuple[Any, ...]) -> List[str]:
        issue_labels=row["fields.labels"].split(",")
        return list(set(issue_labels) & set(request["members"]))
        
    def prompt(self, message: str, options: List[str]) -> str:
        app=Prompt(message, options)
        return app.run()
        
    def jira_update(self, request: ConfigurationType, chosen_option: str, issue_key: str) -> None:
        account: Tuple[Any, ...]=next((account for account in request["accounts"] if "-".join(account["displayName"]) == chosen_option), None)
        
        if not account:
            print(f"Could not find account for {chosen_option}")
            
        response=requests.post(
            f"https://creditonebank.atlassian.net/rest/api/3/issue/{issue_key}",
            auth=HTTPBasicAuth(request["email"], request["token"]),
            headers={
                "Accept": "application/json",
                "Content-Type": "applications/json"
            },
            data=json.dumps({
                "update": {
                    "customfield_10264": [{ "set": { "id": account["accountId"] }}]
                }
            }, cls=DateTimeEncoder),
            verify=False
        )
        
        if response.status_code != 204 and response.status_code != 200:
            print(f"Updating primary developer for {issue_key} was NOT successful")
        
        return None
            # get options from labels
            # present options
            # collect response
            # send update single or bulk via api
            # update row TODO: check what the value would normally be so we can conform to that a little bitty.
        
                
    #     request.log("UpdateDevHandler().handle().")
    #     if not request.proceed:
    #         sys_exit(0, request, "request.proceed is False. Exiting.")
        
    #     if not request.token:
    #         sys_exit(1, request, "Could not find jira api token required for authentication.")
        
    #     if not request.email:
    #         sys_exit(1, request, "Could not find jira email required for authentication.")

    #     for i, responseData in enumerate(request.responseList):
    #         df=pd.json_normalize(responseData.get("issues", []))

    #         for j, row in df.iterrows():
    #             # if a primary developer is already set, skip
    #             if "fields.customfield_10264.displayName" in row and pd.notna(row["fields.customfield_10264.displayName"]) and row["fields.customfield_10264.displayName"] != "":
    #                 continue;
                
    #             labels=row['fields.labels']
    #             labelSet=set(labels)
    #             nameSet=set(request.nameLabels)
    #             intersection=labelSet.intersection(nameSet)

    #             if len(intersection) > 1:
    #                 message=f"Select a primary developer for issue {row["key"]} : "
    #                 options=sorted(list(filter(lambda x: x in request.accountIds, intersection)))
    #                 selection=self.prompt_and_select(options, message) if len(options) > 1 else options[0]
    #                 # update the ticket in jira and in this run
    #                 self.send_update_request(request, selection, row['key'])
    #                 request.responseList[i]["issues"][j]["fields"]["customfield_10264"]=request.accountIds[selection]
        
    #     return super().handle(request)

    # def prompt_and_select(self, options, prompt_message="Select an option"):
    #     """Prompt user to choose primary developer. Save response.

    #     Args:
    #         options (_type_): _description_
    #         prompt_message (str, optional): _description_. Defaults to "Select an option".

    #     Returns:
    #         _type_: _description_
    #     """

    #     click.echo(prompt_message)
    #     for i, option in enumerate(options):
    #         click.echo(f"{i + 1}. {option}")

    #     while True:
    #         try:
    #             selection = int(click.prompt("Enter the number of your selection"))
    #             if 1 <= selection <= len(options):
    #                 return options[selection - 1]
    #             else:
    #                 click.echo("Invalid selection. Please try again.")
    #         except ValueError:
    #             click.echo("Invalid input. Please enter a number.")

    # def send_update_request(self, request, labelName, ticketId):
    #     """Make request to Jira to update the Developer field based on user selection.

    #     Args:
    #         request (_type_): _description_
    #         labelName (_type_): _description_
    #         ticketId (_type_): _description_
    #     """
    #     print(request.accountIds[labelName]["accountId"])
    #     try:
    #         displayName=labelName.replace("-", " ")
    #         response=requests.request(
    #             method="PUT",
    #             url=f"https://creditonebank.atlassian.net/rest/api/3/issue/{ticketId}",
    #             headers={ "Accept": "application/json", "Content-Type": "application/json" },
    #             auth=HTTPBasicAuth(request.email, request.token),
    #             data=json.dumps({
    #                 "update": {
    #                     "customfield_10264": [{ "set": { "id": request.accountIds[labelName]["accountId"] }}]
    #                 }
    #             }),
    #             verify=False
    #         )
            
    #         if response.status_code != 204 and response.status_code != 200:
    #             sys_exit(1, request, f"request failed: \n {response.status_code}, {response.reason}, {response.text}")

    #         request.log(f"Success updating {displayName} as primary developer on ticket: {ticketId}")
    #     except Exception as e:
    #         sys_exit(1, request, f"exception occured processing request: {e}")