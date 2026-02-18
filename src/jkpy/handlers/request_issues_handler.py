from __future__ import annotations
from typing import Dict
from typing import Any
from typing import List
import json
import polars as pl
import requests
from requests.auth import HTTPBasicAuth
from jkpy.handlers.handler import Handler
from jkpy.utils import DateTimeEncoder
from jkpy.utils import Print

class RequestIssuesHandler(Handler):
    def process(self, model: 'AppModel', view: 'AppView') -> None:
        Print.green(f"Collecting Jira issues...")
        
        query: str=self.get_jql_query(model, view)
        all_issues: Dict[str, Any]=self.get_all_issues(query, model, view)
        df: pl.DataFrame=pl.json_normalize(all_issues, infer_schema_length=len(all_issues), strict=False)
        
        model.data["originaldata"]=df
        model.data["tempdata"].append(df)
        
        Print.green(f"All issues received\n")
    
    def get_jql_query(self, model: 'AppModel', view: 'AppView') -> str:
        jql_parts: List[str]=[f"("]
        # labels
        jql_parts.append(f"(labels in ({",".join([f"'{label}'" for label in model.data["labels"]])}))")
        # teams
        jql_parts.append(f" OR ")
        jql_parts.append(f"('Team Name[Dropdown]' in ({",".join([f"'{team}'" for team in model.data["teams"]])})))")
        # statuses
        jql_parts.append(f" AND ")
        jql_parts.append(f"status CHANGED TO ({",".join([f"'{status}'" for status in model.data["statuses"]])})")
        # time range
        jql_parts.append(f" AFTER {model.data["start"].strftime("%Y-%m-%d")} BEFORE {model.data["end"].strftime("%Y-%m-%d")}")
        
        jql="".join(jql_parts)
        Print.green("Jira Query:")
        Print.green(jql)
        
        return jql
    
    def get_all_issues(self, query: str, model: 'AppModel', view: 'AppView') -> Dict[str, Any]:
        all_issues: List[Dict[str, Any]]=[]
        max_results: int=150
        nextPageToken: str=None
        
        while True:
            response: requests.Response=requests.request(
                method="POST",
                url=f"{model.data["host"]}/rest/api/3/search/jql",
                auth=HTTPBasicAuth(model.data["email"], model.data["token"]),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                data=json.dumps({
                    "jql": query,
                    "maxResults": max_results,
                    "nextPageToken": nextPageToken,
                    "fields": ["*all"]
                }, cls=DateTimeEncoder),
                verify=False
            )
            
            if response.status_code != 200:
                raise Exception("/rest/api/3/search/jql", f"status code: {response.status_code}", f"reason: {response.reason}")
            
            responsedata: Dict[str, Any]=response.json()
            issues: List[Dict[str, Any]]=responsedata.get("issues", [])
            all_issues.extend(issues)
            Print.green(f"{len(all_issues)} issues...")
            
            if responsedata.get("isLast") or responsedata.get("nextPageToken") is None:
                break
        
        return all_issues