from jkpy.handlers.base_handler import BaseHandler
from jkpy.configuration import ConfigurationType
import polars as pl

class FilterHandler(BaseHandler):
    """
    Filter all rows for issues in a resolved/done status
    """
    def handle(self, request: ConfigurationType) -> None:
        df=request["temp_data"][-1].filter(pl.col("statuscategorychangedate_datetime") <= pl.col("resolutiondate_datetime"))
        request["temp_data"].append(df)
        
        return super().handle(request)