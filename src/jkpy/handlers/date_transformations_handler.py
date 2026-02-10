from jkpy.handlers.base_handler import BaseHandler
from jkpy.configuration import Configuration
from jkpy.configuration import ConfigurationType
import polars as pl

class DateTransformationsHandler(BaseHandler):
    def handle(self, request: ConfigurationType) -> None:
        df=request["temp_data"][-1]
        # convert/extract to datetime
        df=df.with_columns(
            pl.col("statuscategorychangedate").cast(pl.Datetime).alias("statuscategorychangedate_datetime"),
            pl.col("resolutiondate").cast(pl.Datetime).alias("resolutiondate_datetime")
        )
        # extract month and month name
        df=df.with_columns(
            pl.col("statuscategorychangedate_datetime").dt.month().alias("statuscategorychangedate_num"),
            pl.col("statuscategorychangedate_datetime").dt.month_name().alias("statuscategorychangedate_name"),
            pl.col("resolutiondate_datetime").dt.month().alias("resolutiondate_num"),
            pl.col("resolutiondate_datetime").dt.month_name().alias("resolutiondate_name")
        )
        request["temp_data"].append(df)
        return super().handle(request)
