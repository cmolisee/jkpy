from jkpy.configuration import ConfigurationType
from jkpy.configuration import Configuration
from jkpy.handlers.issues_handler import IssuesHandler
from jkpy.handlers.accounts_handler import AccountsHandler
from jkpy.handlers.validate_developer_handler import ValidateDeveloperHandler
from jkpy.handlers.filter_handler import FilterHandler
from jkpy.handlers.date_transformations_handler import DateTransformationsHandler
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
        # TODO: remove proceed flag
        # TODO: make sure Configurations are initialized as needed
        
        # take the cmd args, update from the saved configs, 
        # and return a full config object include saved configs        
        issues_handler=IssuesHandler() # get all issues
        accounts_handler=AccountsHandler() # get all dpm accounts
        validate_dev_handler=ValidateDeveloperHandler() # validate issues have primary dev
        date_transformation_handler=DateTransformationsHandler() # transform statuscategorychangedate for consumption
        filter_handler=FilterHandler() # filter all issues not in green status
        grouping_handler=GroupingHandler() # group issues by team and member
        aggregation_handler=AggregationHandler() # aggregate metrics on grouping
        excel_output_handler=ExcelOutputHandler() # write to output
        
        issues_handler.set_next(accounts_handler) \
            .set_next(validate_dev_handler) \
            .set_next(date_transformation_handler) \
            .set_next(filter_handler) \
            .set_next(grouping_handler) \
            .set_next(aggregation_handler) \
            .set_next(excel_output_handler)

        return issues_handler
    
__all__=[
    "Handlers"
]