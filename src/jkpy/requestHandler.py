"""jkpy requestHandler"""
# jkpy/reqeustHandler.py

import json
import requests
import urllib3

from jkpy.jiraHandler import JiraHandler
from jkpy.utils import sys_exit

urllib3.disable_warnings()

class RequestHandler(JiraHandler):
    """RequestHandler(JiraHandler)
    
    Concrete implementation of the JiraHandler interface.
    Responsible for making requests and passing results for request objects.
    """

    def handle(self, request):
        """RequestHandler(JiraHandler).hanlde(self, request)
        
        Concrete implementation of the handle() method from JiraHandler.
        Processes all requests and passes results to the next handler.
        This is dependent on requestList from setupHandler().
        """

        request.log("RequestHandler().handle().")
        if not request.proceed:
            sys_exit(0, request, "request.proceed is False. Exiting.")
        
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

        responseList=[]
        try:
            for requestObject in request.requestList:
                nextPageToken=None
                issues=[]
            
                while True:
                    response=requests.request(
                        requestObject.get("method"),
                        requestObject.get("path"),
                        headers=requestObject.get("headers"),
                        params={
                            "jql": requestObject.get("query").get("jql"),
                            "fields": requestObject.get("query").get("fields"),
                            'nextPageToken': nextPageToken,
                        },
                        auth=requestObject.get("auth"),
                        verify=False,
                    )

                    if response.status_code != 200:
                        sys_exit(1, request, f"request failed with {response.status_code}.")

                    data=json.loads(response.text)
                    issues.extend(data.get("issues", []))
                    nextPageToken=data.get("nextPageToken")
                    
                    if not nextPageToken:
                        request.log(f"jira request complete. {len(issues)} issues collected.")
                        break;

                    request.log(f"nextPageToken: {nextPageToken}.")
                
                request.log(f"response data for {requestObject.get("month")} has {len(issues)} issues")
                responseList.append({
                    "month": requestObject.get("month"),
                    "issues": issues
                })

        except Exception as e:
            sys_exit(1, request, f"exception occured processing request: {e}")
        
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

        request.responseList=responseList

        return super().handle(request)
