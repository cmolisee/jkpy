from __future__ import annotations
from typing import Dict
from typing import Any
from typing import Set
from typing import Tuple
import requests
from requests.auth import HTTPBasicAuth
from jkpy.handlers.handler import Handler
from jkpy.utils import Print

class RequestAccountsHandler(Handler):
    def process(self, model: 'AppModel', view: 'AppView') -> None:
        title="Collecting Jira account data >"
        print(title + view.line_break()[len(title):])
        
        cached: Set[Tuple[Any, ...]]=["-".join(dict(account)["displayName"]) for account in model.data["accounts"]]
        accounts_to_get: Set[str]=set(model.data["members"]) - set(cached)
        
        for userDisplayName in accounts_to_get:
            account=self.get_user(userDisplayName, model, view)
            print(f">>> Retrieved account data for {userDisplayName}")
            model.data["accounts"].add(tuple(account))
        
        Print.green(">>> All Jira account data received\n")
    
    def get_user(self, displayName: str, model: 'AppModel', view: 'AppView') -> Dict[str, Any]|None:    
        response: requests.Response=requests.get(
            f"{model.data["host"]}/rest/api/3/user/search?query={displayName}",
            auth=HTTPBasicAuth(model.data["email"], model.data["token"]),
            headers={
                "Accept": "application/json",
                "Content-Type": "applications/json"
            },
            verify=False
        )
        
        if response.status_code != 200:
            raise Exception("Non-200 response from API", response)
        
        res=response.json()
        return res[0] if len(res)>0 else None