from __future__ import annotations
from typing import List
from jkpy.handlers.handler import Handler
from jkpy.prompt_mvc import show_options_prompt
import json
import polars as pl
import requests
from requests.auth import HTTPBasicAuth
from jkpy.utils import DateTimeEncoder
from jkpy.utils import Print

class ValidatePrimaryDeveloperHandler(Handler):
    def process(self, model: 'AppModel', view: 'AppView') -> None:
        view.print_terminal("Validating data for primary developer...\n", Print.GREEN)
        is_missing_primary_developer=pl.col("fields.customfield_10264.displayName").is_null() | (pl.col("fields.customfield_10264.displayName") == "")
        
        validated_df = model.data["originaldata"].with_columns(
            pl.when(is_missing_primary_developer)
            .then(
                pl.struct(["key", "fields.labels"]).map_elements(
                    lambda row: self.prompt_for_primary_developer(row["key"], row["fields.labels"], model, view),
                    return_dtype=str
                )
            )
            .otherwise(pl.col("fields.customfield_10264.displayName"))
            .alias("primary_developer")
        )
        
        model.data["tempdata"].append(validated_df)
        
        view.print_terminal("All data validated for primary developer\n", Print.GREEN)
        
    def jira_update(self, key: str, choice: str, model: 'AppModel', view: 'AppView') -> None:
        account=next((dict(account) for account in model.data["accounts"] if "-".join(dict(account)["displayName"]) == choice), None)
        
        if not account:
            view.print_terminal("WARNING: Could not find account for {choice}\n", Print.YELLOW)
            return
            
        response=requests.post(
            f"https://creditonebank.atlassian.net/rest/api/3/issue/{key}",
            auth=HTTPBasicAuth(model.data["email"], model.data["token"]),
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
            view.print_terminal("Updating primary developer for {key} was NOT successful\n", Print.GREEN)
        
        view.print_terminal("Updated {key} with {choice}\n", Print.GREEN)
    
    def prompt_for_primary_developer(self, key: str, labels: List[str], model: 'AppModel', view: 'AppView') -> str:
        options=list(set(labels) & set(model.data["members"]))
        header=f"Issue {key} is missing the primary developer field. Choose which member to assign as the primary developer:"
        
        if len(options)==0:
            view.print_terminal("WARNING: No primary developer options for issue {key}\n", Print.YELLOW)
            return None
        
        choice=show_options_prompt(header, options)
        if choice:
            self.jira_update(key, choice, model, view)
        
        return choice