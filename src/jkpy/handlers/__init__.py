from jkpy.handlers.request_issues_handler import RequestIssuesHandler
from jkpy.handlers.request_accounts_handler import RequestAccountsHandler
from jkpy.handlers.pre_filter_handler import PreFilterHandler
from jkpy.handlers.preprocessing_date_handler import PreprocessingDateHandler
from jkpy.handlers.preprocessing_team_labels_handler import PreprocessingTeamLabelsHandler
from jkpy.handlers.validate_primary_dev_handler import ValidatePrimaryDeveloperHandler
from jkpy.handlers.grouping_handler import GroupingHandler
from jkpy.handlers.aggregation_handler import AggregationHandler
from jkpy.handlers.excel_output_handler import ExcelOutputHandler

class Handlers:
    @classmethod
    def create_chain(self):
        # TODO: Add 'handlers' as a cmd arg
        # TODO: Add strategy for clearing cached application data
        # TODO: modify Configuration to get, update, and write/save
        # TODO: add HOST to configuration and cmd args
        # TODO: make sure all access to dict or tuples is done with ["key"] and not the dot accessor
        
        # TODO: clean out unsued/commented code
        # TODO: make sure Configurations are initialized as needed
        # TODO: remove warning from requests
        # TODO: Modify output
            # when selecting an option prompt user to choose if they would like to exit (y/n)
                # if yes, clear the options, print and exit
                # if no, collect output to a queue for printing on exit
            # on exit, clear the options, print the logs/queue
              
        request_issues_handler=RequestIssuesHandler()
        request_accounts_handler=RequestAccountsHandler()
        pre_filter_handler=PreFilterHandler()
        preprocessing_date_handler=PreprocessingDateHandler()
        preprocessing_team_labels_handler=PreprocessingTeamLabelsHandler()
        validate_primary_dev_handler=ValidatePrimaryDeveloperHandler()
        grouping_handler=GroupingHandler()
        aggregation_handler=AggregationHandler()
        excel_output_handler=ExcelOutputHandler()
        
        request_issues_handler.set_next(request_accounts_handler) \
            .set_next(pre_filter_handler) \
            .set_next(preprocessing_date_handler) \
            .set_next(preprocessing_team_labels_handler) \
            .set_next(validate_primary_dev_handler) \
            .set_next(grouping_handler) \
            .set_next(aggregation_handler) \
            .set_next(excel_output_handler)

        return request_issues_handler
    
__all__=[
    "Handlers"
]