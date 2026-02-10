from jkpy.handlers.base_handler import BaseHandler
from jkpy.configuration import ConfigurationType

class GroupingHandler(BaseHandler):
    def handle(self, request: ConfigurationType) -> None:
        df=request["temp_data"][-1].group_by([*request["teams"], *request["members"]])
        request["temp_data"].append(df)
        
        return super().handle(request)