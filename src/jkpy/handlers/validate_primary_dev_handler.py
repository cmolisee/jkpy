from __future__ import annotations
from typing import List
from jkpy.handlers.handler import Handler
from jkpy.mvc.options import show_options_prompt
import json
import polars as pl
import requests
from requests.auth import HTTPBasicAuth
from jkpy.utils import DateTimeEncoder
from jkpy.utils import Print
from jkpy.mvc.options import confirm

class ValidatePrimaryDeveloperHandler(Handler):
    def process(self, model: 'AppModel', view: 'AppView') -> None:
        self.model=model
        self.view=view
        
        title="Validating data for primary developer >"
        print(title + view.line_break()[len(title):])
        
        print(">>> Identifying issues with missing primary developer: customfield_10264.displayName")
        null_indices=model.data["tempdata"][-1].with_row_index().filter(pl.col("fields.customfield_10264.displayName").is_null())["index"].to_list()
        
        print(">>> Creating alias for primary developer column: primary_developer")
        data=model.data["tempdata"][-1].to_dict(as_series=False)
        data["primary_developer"]=data["fields.customfield_10264.displayName"].copy()
        
        if not null_indices:
            Print.green(">>> All issues have a primary developer")
            model.data["tempdata"].append(pl.DataFrame(data))
            return
        
        for idx in null_indices:
            choice=self.prompt_action(model.data["tempdata"][-1].row(idx, named=True))
            data["primary_developer"][idx]=choice
        
        model.data["tempdata"].append(pl.DataFrame(data, strict=False))
        Print.green(">>> Primary developer column fully validated\n")
        
    def jira_update(self, key: str, choice: str) -> None:
        account=next((dict(account) for account in self.model.data["accounts"] if "-".join(dict(account)["displayName"]) == choice), None)
        
        if not account:
            Print.yellow(">>> WARNING: Could not find account for {choice}")
            return
            
        response=requests.post(
            f"https://creditonebank.atlassian.net/rest/api/3/issue/{key}",
            auth=HTTPBasicAuth(self.model.data["email"], self.model.data["token"]),
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
            Print.yellow(">>> Updating primary developer for {key} was NOT successful")
        
        print(">>> Updated {key} with {choice}")
    
    def prompt_action(self, row) -> str:
        header=f"\x1b[K\n{Print.MAGENTA}{row["key"]}, {row["fields.summary"]}{Print.NC}\nMissing primary developer, select an option:"
        
        # get disjoint set, default to all members, add None to drop the row
        options=list(set(row["fields.labels"]) & set(self.model.data["members"]))
        options=options if len(options)>0 else self.model.data["members"]
        options.append("Drop This Issue")
        
        # user interaction loop
        choice="None"
        while True:
            choice=show_options_prompt(header, options)
            
            if confirm(f"You selected '{choice}', Are you sure you want to continue?"):
                break; # if confirmed then move on, else retry prompt
            
            # re-render over previous options and confirmation prompts
            print(f"\x1b[{len(options)+len(header.splitlines())+1}A", end="")
            
        # Update Jira
        # 'Drop This Issue' will retain None in the field
        # 'q' or 'Q' should exit the application
        if choice!="Drop This Issue":
            self.jira_update(row["key"], choice)
        
        return choice