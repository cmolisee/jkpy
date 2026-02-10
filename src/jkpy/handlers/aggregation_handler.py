from jkpy.handlers.base_handler import BaseHandler
from jkpy.configuration import ConfigurationType
from typing import Iterable
from datetime import timedelta
import polars as pl
from polars._typing import IntoExpr

class AggregationHandler(BaseHandler):
    def handle(self, request: ConfigurationType) -> None:
        grouping=request["temp_data"][-1]
        
        if not isinstance(grouping, pl.GroupBy):
            raise ValueError(f"Cannot run aggregation on object of type {type(grouping)}. Must be type pl.GroupBy")
        
        aggregators=[]
        aggregators.append(self.get_total_issues_aggregator(request))
        aggregators.append(self.get_story_point_sum_aggregator(request))
        aggregators.append(self.get_total_time_spent_aggregator(request))
        aggregators.append(self.get_total_no_tracking_aggregator(request))
        aggregators.append(self.get_total_enhancements_aggregator(request))
        aggregators.append(self.get_total_bugs_aggregator(request))
        aggregators.append(self.get_total_defects_aggregator(request))
        aggregators.append(self.get_total_spikes_aggregator(request))
        aggregators.append(self.get_story_point_average_aggregator(request))
        aggregators.append(self.get_no_time_tracking_deficit_aggregator(request))
        aggregators.append(self.get_sum_by_labels_aggregator(request))
        
        df=request["temp_data"][-1].agg(aggregators)
        request["temp_data"].append(df)
        return super().handle(request)
    
    def get_total_issues_aggregator(self, request: ConfigurationType) -> IntoExpr | Iterable[IntoExpr]:
        return pl.len().alias('total_issues')

    def get_story_point_sum_aggregator(self, request: ConfigurationType) -> IntoExpr | Iterable[IntoExpr]:
        return pl.col("fields.customfield_10028").sum().alias("story_point_sum")

    def format_time_spent(self, ms: int) -> str:
        total_seconds = ms / 1000.0
        td = timedelta(seconds=total_seconds)
        
        weeks = td.days // 7
        days = td.days % 7
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = td.microseconds // 1000
        
        parts=[""]
        if weeks:
            parts.append(f"{weeks} weeks")
        if days:
            parts.append(f"{days} days")
        if hours:
            parts.append(f"{hours} hours")
        if minutes:
            parts.append(f"{minutes} minutes")
        if seconds:
            parts.append(f"{seconds} seconds")
        if milliseconds:
            parts.append(f"{milliseconds} milliseconds")
        
        return " ".join(parts)
    
    def get_total_time_spent_aggregator(self, request: ConfigurationType) -> IntoExpr:
        return pl.col("fields.timespent").sum().apply(self.format_time_spent).alias("total_time_spent")

    def get_total_no_time_tracking_aggregator(self, request: ConfigurationType) -> IntoExpr:
        return (pl.col("fields.timespent")==0 | pl.col("fields.timespent").is_null()).count().alias("no_time_tracking")

    def get_total_enhancements_aggregator(self, request: ConfigurationType) -> IntoExpr:
        return pl.col("fields.labels").str.contains("enhancement", case=False).alias("total_enhancements")

    def get_total_bugs_aggregator(self, request: ConfigurationType) -> IntoExpr:
        return pl.col("fields.labels").str.contains("bug", case=False).alias("total_bugs")

    def get_total_defects_aggregator(self, request: ConfigurationType) -> IntoExpr:
        return pl.col("fields.labels").str.contains("defect", case=False).alias("total_defects")

    def get_total_spikes_aggregator(self, request: ConfigurationType) -> IntoExpr:
        return pl.col("fields.labels").str.contains("spike", case=False).alias("total_spikes")

    def get_story_point_average_aggregator(self, request: ConfigurationType) -> IntoExpr:
        return pl.col("fields.customfield_10028").mean().alias("story_point_average")

    def get_no_time_tracking_deficit_aggregator(self, request: ConfigurationType) -> IntoExpr:
        total_no_tracking=(pl.col("fields.timespent")==0 | pl.col("fields.timespent").is_null()).count()
        total_issues=pl.len()
        return (round((total_no_tracking / total_issues) * 100, 3)).alias("time_tracking_deficit")
        
    def get_sum_by_labels_aggregator(self, request: ConfigurationType) -> Iterable[IntoExpr]:
        return [pl.col("fields.labels").str.contains(label, case=False).alias(label) for label in request["labels"]]