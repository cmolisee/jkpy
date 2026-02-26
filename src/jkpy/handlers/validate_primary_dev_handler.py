from __future__ import annotations
from jkpy.handlers.handler import Handler
from jkpy.mvc.options import Options
import polars as pl
import httpx
from jkpy.utils import Ansi
from jkpy.mvc.input import Input
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView
import time

class ValidatePrimaryDeveloperHandler(Handler):
    def process(self, model: MenuModel, view: MenuView) -> None:
        self.model=model
        self.view=view
        
        title="Validating data for primary developer >"
        print(title + view.line_break()[len(title):])
        
        print(">>> Identifying issues with missing primary developer: customfield_10264.displayName")
        null_indices=model.data["tempdata"][-1].with_row_index().filter(pl.col("fields.customfield_10264.displayName").is_null())["index"].to_list()
        time.sleep(1)

        print(">>> Creating alias for primary developer column: primary_developer")
        data=model.data["tempdata"][-1].to_dict(as_series=False)
        data["primary_developer"]=data["fields.customfield_10264.displayName"].copy()
        time.sleep(1)
        
        if not null_indices:
            print(Ansi.GREEN+">>> All issues have a primary developer"+Ansi.RESET)
            model.data["tempdata"].append(pl.DataFrame(data, strict=False))
            return
        
        for idx in null_indices:
            choice=self.prompt_action(model.data["tempdata"][-1].row(idx, named=True))
            data["primary_developer"][idx]=choice
        
        model.data["tempdata"].append(pl.DataFrame(data, strict=False))
        print(Ansi.GREEN+"Primary developer column fully validated  ✅"+Ansi.RESET)
        
    def jira_update(self, key: str, choice: str) -> None:
        account=next((dict(account) for account in self.model.data["accounts"] if "-".join(dict(account)["displayName"]) == choice), None)
        
        if not account:
            print(Ansi.YELLOW+">>> WARNING: Could not find account for {choice}"+Ansi.RESET)
            return
            
        response=httpx.post(
            f"https://creditonebank.atlassian.net/rest/api/3/issue/{key}",
            auth=httpx.BasicAuth(self.model.data["email"], self.model.data["token"]),
            headers={
                "Accept": "application/json",
                "Content-Type": "applications/json"
            },
            data={
                "update": {
                    "customfield_10264": [{ "set": { "id": account["accountId"] }}]
                }
            }
        )
        
        if response.status_code != 204 and response.status_code != 200:
            print(Ansi.YELLOW+">>> Updating primary developer for {key} was NOT successful"+Ansi.RESET)
        
        print(">>> Updated {key} with {choice}")
    
    def prompt_action(self, row) -> str:
        header=f"\x1b[K\n{Ansi.MAGENTA}{row["key"]}, {row["fields.summary"]}{Ansi.RESET}\nMissing primary developer, select an option:"
        
        # get disjoint set, default to all members, add None to drop the row
        options=list(set(row["fields.labels"]) & set(self.model.data["members"]))
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
        # 'q' or 'Q' should exit the application
        if choice!="Drop This Issue":
            self.jira_update(row["key"], choice)
        
        return choice