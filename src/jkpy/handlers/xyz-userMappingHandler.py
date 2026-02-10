# from jkpy.handlers.base_handler import JiraHandler
# from jkpy.utils import sys_exit
# from requests.auth import HTTPBasicAuth
# import json
# import requests

# class UserMappingHandler(JiraHandler):
#     """Maps name labels in the config to actual user data from Jira.

#     Args:
#         JiraHandler (_type_): _description_
#     """

#     def handle(self, request):
#         """Handler implementation.

#         Args:
#             request (_type_): _description_

#         Returns:
#             _type_: _description_
#         """

#         request.log("UserMappingHandler().handle().")
#         if not request.proceed:
#             sys_exit(0, request, "request.proceed is False. Exiting.")
        
#         if not request.token:
#             sys_exit(1, request, "Could not find jira api token required for authentication.")
        
#         if not request.email:
#             sys_exit(1, request, "Could not find jira email required for authentication.")

#         accountIds={}
#         try:
#             for nameLabel in request.nameLabels:
#                 queryName=nameLabel.replace("-", ".")
#                 displayName=nameLabel.replace("-", " ")
#                 url=f"https://creditonebank.atlassian.net/rest/api/3/user/search?query={queryName}"

#                 request.log(f"Making request for accountID: {url}")
#                 response=requests.request(
#                     method="GET",
#                     url=url,
#                     headers={ "Accept": "application/json", "Content-Type": "application/json" },
#                     auth=HTTPBasicAuth(request.email, request.token),
#                     verify=False
#                 )

#                 if response.status_code != 200:
#                     sys_exit(1, request, f"request failed with {response.status_code}.")

#                 data=json.loads(response.text)
#                 userData=next((user for user in data if displayName in user["displayName"]), None)

#                 if userData == None:
#                     request.log(f"No user account data exists for name label: {nameLabel}, query: {queryName}")
#                     continue;
                
#                 # developer field uses 10264
#                 accountIds[nameLabel]=userData

#         except Exception as e:
#             sys_exit(1, request, f"exception occured processing request: {e}")

#         request.accountIds=accountIds
#         return super().handle(request)