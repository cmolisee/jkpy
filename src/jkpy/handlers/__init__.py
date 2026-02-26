from jkpy.handlers.request_issues_handler import RequestIssuesHandler
from jkpy.handlers.request_accounts_handler import RequestAccountsHandler
from jkpy.handlers.raw_data_filter import RawDataFilter
from jkpy.handlers.preprocessing_date_handler import PreprocessingDateHandler
from jkpy.handlers.preprocessing_dev_labels_handler import PreprocessingDevLabelHandler
from jkpy.handlers.validate_primary_dev_handler import ValidatePrimaryDeveloperHandler
from jkpy.handlers.primary_dev_filter import PrimaryDevFilter
from jkpy.handlers.grouping_handler import GroupingHandler
from jkpy.handlers.aggregation_handler import AggregationHandler
from jkpy.handlers.excel_output_handler import ExcelOutputHandler

class Handlers:
    @classmethod
    def create_chain(cls):
        request_issues_handler=RequestIssuesHandler()
        request_accounts_handler=RequestAccountsHandler()
        raw_data_filter=RawDataFilter()
        preprocessing_date_handler=PreprocessingDateHandler()
        preprocessing_dev_labels_handler=PreprocessingDevLabelHandler()
        validate_primary_dev_handler=ValidatePrimaryDeveloperHandler()
        primary_dev_filter=PrimaryDevFilter()
        grouping_handler=GroupingHandler()
        aggregation_handler=AggregationHandler()
        excel_output_handler=ExcelOutputHandler()
        
        request_issues_handler.set_next(request_accounts_handler) \
            .set_next(raw_data_filter) \
            .set_next(preprocessing_date_handler) \
            .set_next(preprocessing_dev_labels_handler) \
            .set_next(validate_primary_dev_handler) \
            .set_next(primary_dev_filter) \
            .set_next(grouping_handler) \
            .set_next(aggregation_handler) \
            .set_next(excel_output_handler)

        return request_issues_handler
    
__all__=[
    "Handlers"
]