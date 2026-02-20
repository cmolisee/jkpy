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
        title="Collecting Jira issues >"
        print(title + view.line_break()[len(title):])
        
        query: str=self.get_jql_query(model, view)
        all_issues: Dict[str, Any]=self.get_all_issues(query, model, view)
        df: pl.DataFrame=pl.json_normalize(all_issues, infer_schema_length=len(all_issues), strict=False)
        
        model.data["originaldata"]=df
        model.data["tempdata"].append(df)
    
    def get_jql_query(self, model: 'AppModel', view: 'AppView') -> str:
        jql_parts: List[str]=[f"("]
        # labels or teams
        jql_parts.append(f"(labels in ({",".join([f"'{label}'" for label in model.data["members"]])}))")
        jql_parts.append(f" OR ")
        jql_parts.append(f"('Team Name[Dropdown]' in ({",".join([f"'{team}'" for team in model.data["teams"]])})))")
        # labels to ignore
        jql_parts(f" AND ")
        jql_parts(f" labels not in ({",".join([f"'{label}'" for label in model.data["ignore_labels"]])})")
        # ticket types
        jql_parts.append(f" AND ")
        jql_parts.append(f"type in (Story, Task, Bug, Enhancement)")
        # statuses
        jql_parts.append(f" AND ")
        jql_parts.append(f"status CHANGED TO ({",".join([f"'{status}'" for status in model.data["statuses"]])})")
        # time range
        jql_parts.append(f" AFTER {model.data["start"].strftime("%Y-%m-%d")} BEFORE {model.data["end"].strftime("%Y-%m-%d")}")
        
        jql="".join(jql_parts)
        print(">>> Building JQL...")
        
        return jql
    
    def get_all_issues(self, query: str, model: 'AppModel', view: 'AppView') -> Dict[str, Any]:
        all_issues: List[Dict[str, Any]]=[]
        nextPageToken: str=None
        idx=1
        
        while True:
            print(f">>> [Request {idx}]...")
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
                    "maxResults": 150, # API may return fewer
                    "nextPageToken": nextPageToken,
                    "fields": ["*all"]
                }, cls=DateTimeEncoder),
                verify=False
            )
            
            if response.status_code != 200:
                raise Exception("/rest/api/3/search/jql", f"status code: {response.status_code}", f"reason: {response.reason}")
            
            responsedata: Dict[str, Any]=response.json()
            nextPageToken=responsedata.get("nextPageToken", None)
            issues: List[Dict[str, Any]]=responsedata.get("issues", [])
            all_issues.extend(issues)
            idx+=1
            
            if responsedata.get("isLast", False) or nextPageToken is None:
                Print.green(f">>> All issues collected")
                Print.green(f">>> Rows: {len(all_issues)} \tColumns: {len(all_issues[0].keys())}\n")
                break
        
        return all_issues