"""jkpy userMappingHandler"""
# jkpy/userMappingHandler.py

import json
import requests

from jkpy.jiraHandler import JiraHandler
from jkpy.utils import sys_exit
from requests.auth import HTTPBasicAuth


class UserMappingHandler(JiraHandler):
    """UserMappingHandler(JiraHandler)
    
    Concrete implementation of the JiraHandler interface.
    Makes requests to Jira to map name labels to userID's.
    """

    def handle(self, request):
        """UserMappingHandler(JiraHandler).hanlde(self, request)
        
        Concrete implementation of the handle() method from JiraHandler.
        Makes requests to Jira to map name labels to userID's.
        """

        request.log("UserMappingHandler().handle().")
        if not request.proceed:
            sys_exit(0, request, "request.proceed is False. Exiting.")
        
        if not request.token:
            sys_exit(1, request, "Could not find jira api token required for authentication.")
        
        if not request.email:
            sys_exit(1, request, "Could not find jira email required for authentication.")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

        accountIds={}
        try:
            for nameLabel in request.nameLabels:
                queryName=nameLabel.replace("-", ".")
                displayName=nameLabel.replace("-", " ")
                url=f"https://creditonebank.atlassian.net/rest/api/3/user/search?query={queryName}"

                request.log(f"Making request for accountID: {url}")
                response=requests.request(
                    method="GET",
                    url=url,
                    headers={ "Accept": "application/json", "Content-Type": "application/json" },
                    auth=HTTPBasicAuth(request.email, request.token),
                    verify=False
                )

                if response.status_code != 200:
                    sys_exit(1, request, f"request failed with {response.status_code}.")

                data=json.loads(response.text)
                userData=next((user for user in data if displayName in user["displayName"]), None)

                if userData == None:
                    request.log(f"No user account data exists for name label: {nameLabel}, query: {queryName}")
                    continue;
                
                # developer field uses 10264
                accountIds[nameLabel]=userData

        except Exception as e:
            sys_exit(1, request, f"exception occured processing request: {e}")

        request.accountIds=accountIds

        return super().handle(request)