from typing import Dict
from typing import Any
from typing import Set
from typing import Tuple
import requests
from requests.auth import HTTPBasicAuth
from jkpy.configuration import ConfigurationType
from jkpy.handlers.base_handler import BaseHandler

class AccountsHandler(BaseHandler):
    def handle(self, request: ConfigurationType) -> None:
        cached: Set[Tuple[Any, ...]]=["-".join(account["displayName"]) for account in request["accounts"]]
        accounts_to_get: Set[str]=set(request["members"]) - set(cached)
        
        for userDisplayName in accounts_to_get:
            account=self.get_user(request, userDisplayName)
            request["accounts"].add(account)
        
        return super().handle(request)
    
    def get_user(self, request: ConfigurationType, displayName: str) -> Dict[str, Any]|None:
        # TODO: add HOST to configuration
        HOST="https://creditonebank.atlassian.net"
        
        response: requests.Response=requests.get(
            f"{HOST}/rest/api/3/user/search?query={displayName}",
            auth=HTTPBasicAuth(request["email"], request["token"]),
            headers={
                "Accept": "application/json",
                "Content-Type": "applications/json"
            },
            verify=False
        )
        
        if response.status_code != 200:
            raise Exception("Non-200 response from API", response)
        
        data=response.json()
        return data[0] if len(data)>0 else None