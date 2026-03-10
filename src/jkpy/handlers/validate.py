from __future__ import annotations
import json
from jkpy.handlers.handler import Handler
from jkpy.mvc.options import Options
import polars as pl
import httpx
from jkpy.utils import Ansi
from jkpy.mvc.input import Input
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView
import time

class Validate(Handler):
    """validates data, updates primary devs, and/or notifies of missing fields."""
    def process(self, model: MenuModel, view: MenuView) -> None:
        self.model=model
        self.view=view
        
        title="Validating data for primary developer >"
        print(title + view.line_break()[len(title):])
        
        print(">>> Searching for missing primary developers...")
        null_indices=model.data["data_frames"]["normalized"].with_row_index().filter(
            pl.col("primary_developer").is_null()
        )["index"].to_list()
        time.sleep(1.5)
        
        pd_updates={}
        for idx in null_indices:
            choice=self.prompt_action(model.data["data_frames"]["normalized"].row(idx, named=True))
            pd_updates[idx]=choice
        
        if len(pd_updates)>0:
            s=model.data["data_frames"]["normalized"]["primary_developer"].clone()
            model.data["data_frames"]["normalized"]=model.data["data_frames"]["normalized"].with_columns(
                pl.Series("primary_developer", s.scatter(list(pd_updates.keys()), list(pd_updates.values())))
            )
            
        print(">>> Searching for missing labels...")
        missing_label=model.data["data_frames"]["normalized"].with_row_index().filter(
            pl.col("developers").len==0
        )["key"].to_list()
        time.sleep(1.5)
        
        for key in missing_label:
            print(Ansi.YELLOW+f"Issue {key} is missing a label...")
        
        if len(missing_label)>0:
            print(Ansi.YELLOW+f"\nPlease fix all missing labels listed above and re-run to avoid incorrect data and results.")
            import sys
            sys.exit(0)
            
        print(Ansi.GREEN+"All issues validated  ✅\n"+Ansi.RESET)
        
    def jira_update(self, key: str, choice: str) -> None:
        account=None
        for acct in self.model.data["accounts"]:
            if choice.replace("-", " ")==acct["displayName"]:
                account=acct
                break
        
        if not account:
            print(Ansi.YELLOW+f">>> WARNING: Could not find account for {choice}"+Ansi.RESET)
            return
        
        with httpx.Client(verify=False) as client:
            response=client.put(
                f"https://creditonebank.atlassian.net/rest/api/3/issue/{key}",
                auth=httpx.BasicAuth(self.model.data["email"], self.model.data["token"]),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"},
                content=json.dumps({
                    "fields": {
                        "customfield_10264": {
                            "accountId": account["accountId"]
                        }
                    }
                })
            )
        
        if response.status_code != 204 and response.status_code != 200:
            print(Ansi.YELLOW+f">>> Updating primary developer for {key} was NOT successful"+Ansi.RESET)
        else:
            print(f">>> Updated {key} with {choice}")
    
    def prompt_action(self, row) -> str:
        header=f"\x1b[K\n{Ansi.MAGENTA}{row["key"]}, {row["summary"]}{Ansi.RESET}\nMissing primary developer, select an option:"
        
        # get disjoint set, default to all members, add None to drop the row
        options=list(set(row["labels"]) & set(self.model.data["members"]))
        options=options if len(options)>0 else self.model.data["members"]
        options.append("Drop This Issue")
        
        # user interaction loop
        choice="None"
        while True:
            choice=Options.select(header, options)[0]
            
            if Input.confirm(f"You selected '{choice}', Are you sure you want to continue?"):
                break; # if confirmed then move on, else retry prompt
            
            # re-render over previous options and confirmation prompts
            print(f"\x1b[{len(options)+len(header.splitlines())+1}A", end="")
            
        # Update Jira
        # 'Drop This Issue' will retain None in the field
        if choice!="Drop This Issue":
            self.jira_update(row["key"], choice)
        
        return None if choice=="Drop This Issue" else choice