from jkpy.handlers.request_issues import RequestIssues
from jkpy.handlers.request_accounts import RequestAccounts
from jkpy.handlers.normalize import Normalize
from jkpy.handlers.validate import Validate
from jkpy.handlers.filter import Filter
from jkpy.handlers.metrics import Metrics
from jkpy.handlers.excel_output_handler import ExcelOutputHandler

class Handlers:
    @classmethod
    def create_chain(cls):
        handlers={
            0: RequestIssues(),
            1: RequestAccounts(),
            2: Normalize(),
            3: Validate(),
            4: Filter(),
            5: Metrics(),
            6: ExcelOutputHandler(),
        }
        
        chain=handlers[0]
        chain.set_next(handlers[1]) \
            .set_next(handlers[2]) \
            .set_next(handlers[3]) \
            .set_next(handlers[4]) \
            .set_next(handlers[5]) \
            .set_next(handlers[6])
        
        # request_issues_handler.set_next(request_accounts_handler) \
        #     .set_next(raw_data_filter) \
        #     .set_next(preprocessing_date_handler) \
        #     .set_next(preprocessing_dev_labels_handler) \
        #     .set_next(validate_primary_dev_handler) \
        #     .set_next(primary_dev_filter) \
        #     .set_next(grouping_handler) \
        #     .set_next(aggregation_handler) \
        #     .set_next(excel_output_handler)

        return chain
    
__all__=[
    "Handlers"
]