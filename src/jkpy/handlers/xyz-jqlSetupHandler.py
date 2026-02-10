# from datetime import date
# from dateutil.rrule import *
# from jkpy.handlers.base_handler import JiraHandler
# from jkpy.types import RequestObject
# from jkpy.utils import get_date_parts, sys_exit
# from requests.auth import HTTPBasicAuth
# import calendar
# import io

# class JqlSetupHandler(JiraHandler):
#     """Handles the setup of the Jira API requests.

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

#         request.log("SetupHandler().handle().")
#         if not request.proceed:
#             sys_exit(0, request, "request.proceed is False. Exiting.")
        
#         if not request.token:
#             sys_exit(1, request, "Could not find jira api token required for authentication.")
        
#         if not request.email:
#             sys_exit(1, request, "Could not find jira email required for authentication.")

#         currentYear=date.today().year
#         startYear,startMonth,startDay=get_date_parts(request.startDate)
#         endYear,endMonth,endDay=get_date_parts(request.endDate)

#         # get user defined start date or first day of year
#         startDate=date(
#             startYear if startYear else currentYear, 
#             startMonth if startMonth else 1, 
#             startDay if startDay else 1
#         )
#         # get user defined end date or last day of year
#         endDate=date(
#             endYear if endYear else currentYear, 
#             endMonth if endMonth else 12, 
#             endDay if endDay else 31
#         )

#         # API request fields
#         path=f"https://creditonebank.atlassian.net/rest/api/3/search/jql"
#         headers={ "Accept": "application/json" }
#         auth=HTTPBasicAuth(request.email, request.token)
#         fields='customfield_10264,resolutiondate,updated,assignee,created,customfield_10003,customfield_10014,customfield_10235,customfield_10303,customfield_10157,fixVersion,labels,status,statuscategorychangedate,key,customfield_10020,customfield_10028,timespent'

#         requestList: list[RequestObject]=[]
#         monthsInRange=enumerate(rrule(MONTHLY, dtstart=startDate, until=endDate))
#         for _, dt in monthsInRange:
#             try:
#                 _, lastDayOfMonth=calendar.monthrange(dt.year, dt.month)
#                 if startDate.day > 1:
#                     formattedStartDate=dt.replace(day=startDate.day).strftime("%Y-%m-%d")
#                 else: 
#                     formattedStartDate=dt.replace(day=1).strftime("%Y-%m-%d")

#                 if (endMonth == dt.month and endDate.day < lastDayOfMonth):
#                     formattedEndDate=dt.replace(day=endDate.day).strftime("%Y-%m-%d")
#                 else:
#                     formattedEndDate=dt.replace(day=lastDayOfMonth).strftime("%Y-%m-%d")
                    
#                 # JQL query to get all tickets that
#                 # 1) have one of the name labels in it
#                 # or
#                 # 2) are assigned to one of the team labels with a status changed to one of the status labels
#                 # both between the after and before dates
#                 jql=io.StringIO()
#                 jql.write(f"((labels in ({', '.join(n for n in request.nameLabels)})) ")
#                 jql.write(f"OR (\"Team Name[Dropdown]\" in ({', '.join(str(s) for s in request.teamLabels)}))) ")
#                 jql.write("AND status CHANGED TO ")
#                 jql.write(f"({', '.join(str(s) for s in request.statusTypes)}) ") # filter by status type changed too
#                 jql.write(f"AFTER {formattedStartDate} ") # status change date from
#                 jql.write(f"BEFORE {formattedEndDate} ") # status change date too
#                 jql.write("ORDER BY created DESC")

#                 request.log(f"JQL for {calendar.month_name[dt.month]}: {jql.getvalue()}.")

#                 requestList.append({
#                     "month": calendar.month_name[dt.month],
#                     "type": "default",
#                     "method": "GET",
#                     "path": path,
#                     "headers": headers,
#                     "query": {
#                         'jql': jql.getvalue(),
#                         'fields': fields
#                     },
#                     "auth": auth,
#                 })

#             except Exception as e:
#                 sys_exit(1, request, f"exception occured building request data for {calendar.month_name[dt.month]}: {e}")

#         request.requestList=requestList
#         return super().handle(request)

# # Get all the schema for epic,story,bug,task
# # curl --location 'https://creditonebank.atlassian.net/rest/api/3/issue/createmeta?projectKeys=DPM&expand=projects.issuetypes.fields' \
# # --header 'Authorization: Basic Y29keS5tb2xpc2VlQGNyZWRpdG9uZS5jb206QVRBVFQzeEZmR0YwcWtDQmdsN3c5Q0pOYVlFV1VONFdPdmxHTzlSVUp3M2JQY0xjNV9Wbnhzem1mNzdCN3diUVZRMm1CU192MHI4MUJYZmMtRlRWSm94ZHBPdXZ4emtIZkFUNHhJaV9yYzVlTWFESG9KRFd3ZWVuMXFqNjdDY21yZ2MtdGk3cFN6VUtiX0hVNDFES1RoNEdiSHluVW5CWUZiZkpNREQwbFRYX1JnX0tSM0NpUHJFPTFDMEQ2REI2'
# # response.project.issuetypes
# # get story,bug,epic,task
# # get fields.key, fields.name of each to compile a list

# # we can save this schema to validate that future requests have these columns

# # aggregateprogress:"Σ Progress"
# # aggregatetimeestimate:"Σ Remaining Estimate"
# # aggregatetimeoriginalestimate:"Σ Original Estimate"
# # aggregatetimespent:"Σ Time Spent"
# # assignee:"Assignee"
# # attachment:"Attachment"
# # comment:"Comment"
# # components:"Components"
# # created:"Created"
# # creator:"Creator"
# # customfield_10000:"Development"
# # customfield_10001:"Team"
# # customfield_10002:"Organizations"
# # customfield_10003:"Approvers"
# # customfield_10004:"Impact"
# # customfield_10005:"Change type"
# # customfield_10006:"Change risk"
# # customfield_10007:"Change reason"
# # customfield_10008:"Change start date"
# # customfield_10009:"Change completion date"
# # customfield_10010:"Request Type"
# # customfield_10014:"Epic Link"
# # customfield_10015:"Start date"
# # customfield_10016:"Story point estimate"
# # customfield_10017:"Issue color"
# # customfield_10018:"Parent Link"
# # customfield_10019:"Rank"
# # customfield_10020:"Sprint"
# # customfield_10021:"Flagged"
# # customfield_10022:"Target start"
# # customfield_10023:"Target end"
# # customfield_10024:"[CHART] Date of First Response"
# # customfield_10025:"[CHART] Time in Status"
# # customfield_10028:"Story Points"
# # customfield_10031:"C1-Consumer Impact"
# # customfield_10032:"C1-Audit and Compliance"
# # customfield_10033:"C1-BR Related Work Order"
# # customfield_10035:"C1-Event Policy (SLA)"
# # customfield_10038:"C1-Release Date"
# # customfield_10039:"C1-Link to FootPrint"
# # customfield_10040:"C1-Type"
# # customfield_10041:"C1-Priority"
# # customfield_10042:"C1-Created On"
# # customfield_10043:"C1-Capability"
# # customfield_10044:"C1-Expected SLA"
# # customfield_10046:"Requester Department"
# # customfield_10047:"Project Classification"
# # customfield_10048:"Data Sources"
# # customfield_10049:"Has Hard Deadline"
# # customfield_10050:"Scope"
# # customfield_10051:"Business Benefit"
# # customfield_10052:"C1-WO Type"
# # customfield_10054:"Requestor Name"
# # customfield_10057:"File Drop Location"
# # customfield_10058:"Processing Frequency"
# # customfield_10059:"File Format"
# # customfield_10060:"C1-Solution"
# # customfield_10065:"C1-Reporter"
# # customfield_10066:"Revision"
# # customfield_10067:"Begin Date"
# # customfield_10068:"End Date"
# # customfield_10071:"C1-Warranty"
# # customfield_10082:"Delivery Date(s)"
# # customfield_10083:"Blocked"
# # customfield_10087:"Project Sponsor"
# # customfield_10088:"Date Submitted"
# # customfield_10089:"Label Name"
# # customfield_10090:"Scope Type"
# # customfield_10091:"Issue Category"
# # customfield_10092:"Date Issue First Appeared "
# # customfield_10094:"Department(s) Affected"
# # customfield_10095:"Process ID"
# # customfield_10097:"Risk Indicator"
# # customfield_10098:"Impact"
# # customfield_10099:"Short Term Solution"
# # customfield_10101:"Long Term Solution"
# # customfield_10102:"Current Update"
# # customfield_10103:"QA Tester"
# # customfield_10104:"Developer"
# # customfield_10105:"Parent Process ID"
# # customfield_10118:"Department(s) Accountable"
# # customfield_10119:"Identifying Department"
# # customfield_10121:"Budget"
# # customfield_10140:"Project Source"
# # customfield_10141:"Roll Back Plan"
# # customfield_10142:"Estimators/Simulation Needed"
# # customfield_10143:"SNOW Ticket Number"
# # customfield_10145:"Other Systems Interactions"
# # customfield_10146:"Scope of Change"
# # customfield_10147:"Business Case"
# # customfield_10148:"As Is Structure"
# # customfield_10149:"To Be Structure"
# # customfield_10150:"Requirements Detail & Supporting Information"
# # customfield_10151:"List of Programs Affected"
# # customfield_10152:"UAT Test Plan, Scenarios, & Testers"
# # customfield_10153:"Estimated Benefit"
# # customfield_10154:"Implementation Approvals (PEGA)"
# # customfield_10155:"Go Live Date"
# # customfield_10156:"Priority"
# # customfield_10157:"Acceptance Criteria"
# # customfield_10158:"Acceptance Criteria approved by Business"
# # customfield_10196:"Project Dependencies"
# # customfield_10211:"Emergency"
# # customfield_10212:"Other Systems Interactions"
# # customfield_10213:"Calls Expected"
# # customfield_10214:"Requires a CS Procedure Update"
# # customfield_10215:"Requires Ops Approval"
# # customfield_10216:"Emergency Rule"
# # customfield_10217:"Ruleset Area"
# # customfield_10218:"Queue Area"
# # customfield_10219:"RSEALL - Priority"
# # customfield_10220:"Action Number"
# # customfield_10221:"Rule Area"
# # customfield_10222:"Fraud Strategy Group"
# # customfield_10223:"Memo"
# # customfield_10224:"L/S Volume Expected"
# # customfield_10225:"Exact Calls Expected"
# # customfield_10226:"Simulation Requested"
# # customfield_10227:"Simulation Total Transaction"
# # customfield_10228:"Simulation Impacted Accounts"
# # customfield_10229:"Simulation Dollar Amount"
# # customfield_10230:"Total Transaction"
# # customfield_10231:"Total Dollar Amount"
# # customfield_10232:"Total Impacted Accounts"
# # customfield_10233:"Distinct Cards Affected"
# # customfield_10234:"Status Date"
# # customfield_10235:"Team Name"
# # customfield_10240:"Test User"
# # customfield_10241:"Initiative Name"
# # customfield_10242:"Requester Dept"
# # customfield_10243:"Key Stakeholders"
# # customfield_10244:"Expected End-State"
# # customfield_10245:"Key Outcomes Expected"
# # customfield_10246:"Leading Indicators"
# # customfield_10247:"In Scope"
# # customfield_10248:"Out of Scope"
# # customfield_10249:"Nonfunctional Requirements"
# # customfield_10250:"Cost"
# # customfield_10251:"ROI"
# # customfield_10253:"C1 Root Cause"
# # customfield_10254:"Requester VP"
# # customfield_10264:"Developer"
# # customfield_10265:"QA"
# # customfield_10266:"UAT"
# # customfield_10279:"Request participants"
# # customfield_10282:"Reported Date"
# # customfield_10283:"Owner/Assignment"
# # customfield_10284:"Priority - Business"
# # customfield_10285:"Priority - Fraud Risk"
# # customfield_10286:"Priority - T&F"
# # customfield_10287:"Priority - Pega"
# # customfield_10288:"Tag"
# # customfield_10289:"Intake #"
# # customfield_10290:"Priority Number"
# # customfield_10291:"Required to Retire FT"
# # customfield_10292:"Benefit"
# # customfield_10293:"Work-around Available"
# # customfield_10295:"Business Impact"
# # customfield_10296:"Customer Impact"
# # customfield_10297:"Issue Impact"
# # customfield_10298:"Found after upgrade"
# # customfield_10299:"Story ID"
# # customfield_10300:"Footprints ID"
# # customfield_10301:"Quavo ID"
# # customfield_10302:"Quavo Feedback"
# # customfield_10303:"Product Owner"
# # customfield_10304:"Satisfaction"
# # customfield_10305:"Satisfaction date"
# # customfield_10306:"Request language"
# # customfield_10307:"Affected services"
# # customfield_10308:"Content Links"
# # customfield_10309:"Development Links"
# # customfield_10327:"Open forms"
# # customfield_10328:"Submitted forms"
# # customfield_10329:"Locked forms"
# # customfield_10330:"Total forms"
# # customfield_10331:"Severity"
# # customfield_10333:"Platform"
# # customfield_10334:"Category"
# # customfield_10336:"Release Date"
# # customfield_10337:"Email Proof Due Date"
# # customfield_10338:"Audience File Due Date:"
# # customfield_10339:"Estimated Audience Count:"
# # customfield_10340:"Audience Criteria:"
# # customfield_10341:"Audience File Name:"
# # customfield_10342:"Reason Code In Data File:"
# # customfield_10343:"Fields Populated in Date File:"
# # customfield_10344:"Folder Path (for assets, images, icons, mockups, etc, data file and for channel team to drop proofs):"
# # customfield_10345:"Subject Line:"
# # customfield_10346:"Preheader:"
# # customfield_10348:"Is This a Test?"
# # customfield_10349:"Headline Copy"
# # customfield_10350:"Body Copy"
# # customfield_10351:"Call To Action Copy"
# # customfield_10352:"Call To Action URL"
# # customfield_10353:"If yes, what is being tested and how will it be measured"
# # customfield_10354:"Email Disclaimer/T&C’s:"
# # customfield_11385:"Start Date/Time"
# # customfield_11386:"Button Copy"
# # customfield_11387:"Button Action"
# # customfield_11388:"Push Action"
# # customfield_11389:"Repeat this Message"
# # customfield_11390:"Minimum Time between Displays"
# # customfield_11391:"Screen to Trigger"
# # customfield_11392:"Frequency"
# # customfield_11393:"Does a workaround exist? (If Not Applicable, Please Put N/A)"
# # customfield_11394:"Is this date/time sensitive?"
# # customfield_11395:"Value Matrix score"
# # customfield_11396:"Fix Details"
# # customfield_11397:"Environment Affected"
# # customfield_11398:"Design"
# # customfield_11399:"QA Integration"
# # customfield_11414:"Project overview key"
# # customfield_11415:"Project overview status"
# # customfield_11417:"Initial Payment"
# # customfield_11418:"Reimbursement Amount"
# # customfield_11419:"Other Job Found"
# # customfield_11422:"Sentiment"
# # customfield_11423:"Goals"
# # description:"Description"
# # duedate:"Due date"
# # environment:"Environment"
# # fixVersions:"Fix versions"
# # issuelinks:"Linked Issues"
# # issuerestriction:"Restrict to"
# # issuetype:"Issue Type"
# # labels:"Labels"
# # lastViewed:"Last Viewed"
# # parent:"Parent"
# # priority:"Priority"
# # progress:"Progress"
# # project:"Project"
# # reporter:"Reporter"
# # resolution:"Resolution"
# # resolutiondate:"Resolved"
# # security:"Security Level"
# # status:"Status"
# # statuscategorychangedate:"Status Category Changed"
# # subtasks:"Sub-tasks"
# # summary:"Summary"
# # timeestimate:"Remaining Estimate"
# # timeoriginalestimate:"Original estimate"
# # timespent:"Time Spent"
# # timetracking:"Time tracking"
# # updated:"Updated"
# # versions:"Affects versions"
# # votes:"Votes"
# # watches:"Watchers"
# # worklog:"Log Work"
# # workratio:"Work Ratio"