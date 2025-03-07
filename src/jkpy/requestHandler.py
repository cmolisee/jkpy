from jkpy.jiraHandler import JiraHandler
from jkpy.utils import sys_exit
import json
import pandas as pd
import requests
import urllib3

# silence console output from this lib from requests
urllib3.disable_warnings()

class RequestHandler(JiraHandler):
    """Makes requests to jira and handles the raw response.

    Args:
        JiraHandler (_type_): _description_
    """

    def handle(self, request):
        """Handler implementation.

        Args:
            request (_type_): _description_

        Returns:
            _type_: _description_
        """

        request.log("RequestHandler().handle().")
        if not request.proceed:
            sys_exit(0, request, "request.proceed is False. Exiting.")

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
                
                df=pd.json_normalize(issues)
                for _,row in df.iterrows():
                    if not pd.isna(row["fields.customfield_10264"]):
                        print(row["fields.customfield_10264"])

        except Exception as e:
            sys_exit(1, request, f"exception occured processing request: {e}")
        
        request.responseList=responseList
        return super().handle(request)
