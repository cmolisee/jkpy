from typing import Dict
from typing import Any
from typing import List
import json
import polars as pl
import requests
from requests.auth import HTTPBasicAuth
from jkpy.configuration import ConfigurationType
from jkpy.handlers.base_handler import BaseHandler
from jkpy.utils import DateTimeEncoder

class IssuesHandler(BaseHandler):
    def handle(self, request: ConfigurationType) -> None:
        query: str=self.get_jql_query(request)
        all_issues: Dict[str, Any]=self.get_all_issues(request, query)
        # flatten data for dataframe compatibility 
        flattened_issues: Dict[str, Any]=[self.flatten_json(issue) for issue in all_issues]
        df: pl.DataFrame=pl.DataFrame(flattened_issues)
        
        request["original_data"]=df
        request["temp_data"].append(df)
        
        return super().handle(request)
    
    def get_jql_query(self, request: ConfigurationType) -> str:
        jql_parts: List[str]=[f"("]
        # labels
        jql_parts.append(f"(labels in ({",".join([f"'{label}'" for label in request["labels"]])}))")
        # teams
        jql_parts.append(f" OR ")
        jql_parts.append(f"('Team Name[Dropdown]' in ({",".join([f"'{team}'" for team in request["teams"]])})))")
        # statuses
        jql_parts.append(f" AND ")
        jql_parts.append(f"status CHANGED TO ({",".join([f"'{status}'" for status in request["statuses"]])})")
        # time range
        jql_parts.append(f" AFTER {request["start"].strftime("%Y-%m-%d")} BEFORE {request["end"].strftime("%Y-%m-%d")}")
        
        jql="".join(jql_parts)
        
        print(f"[VERBOSE] JQL is {jql}")
            
        return jql
    
    def get_all_issues(self, request: ConfigurationType, query: str) -> Dict[str, Any]:
        # fields='customfield_10264,resolutiondate,updated,assignee,created,customfield_10003,customfield_10014,customfield_10235,customfield_10303,customfield_10157,fixVersion,labels,status,statuscategorychangedate,key,customfield_10020,customfield_10028,timespent'
                
        # TODO: add HOST to configuration
        HOST="https://creditonebank.atlassian.net"
        
        all_issues: List[Dict[str, Any]]=[]
        max_results: int=150
        nextPageToken=None
        
        while True:
            print(f"PRINTING REQUEST RESPONSE")
                
            response: requests.Response=requests.request(
                method="POST",
                url=f"{HOST}/rest/api/3/search/jql",
                auth=HTTPBasicAuth(request["email"], request["token"]),
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
                # this might need to be a break; instead of exception
                print(response.status_code)
                print(response.reason)
                print(response.request.body)
                raise Exception("Non-200 response from API", response)
            
            response_data: Dict[str, Any]= response.json()
            issues: List[Dict[str, Any]]=response_data.get("issues", [])
            all_issues.extend(issues)
            nextPageToken+=response_data.get("nextPageToken")
            print(f"total issues: {len(all_issues)}")
            print(f"nextPageToken: {nextPageToken}")
            if nextPageToken is None:
                break
            
        return all_issues
    
    def flatten_json(self, obj: Any, prefix: str="") -> Any:
        flattened_dict = {}
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{prefix}.{key}" if prefix else key
                flattened_dict.update(self.flatten_json(value, new_key))
                
        elif isinstance(obj, list):
            if all(isinstance(item, (int, float, str, bool, type(None))) for item in obj):
                flattened_dict[prefix]=",".join(obj)
                
            for item in obj:
                flattened_dict.update(self.flatten_json(item, prefix))
                
        else:
            flattened_dict[prefix]=obj
            
        return flattened_dict