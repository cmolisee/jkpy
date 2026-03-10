from __future__ import annotations
from jkpy.handlers.handler import Handler
from jkpy.utils import Ansi
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView
import time
import polars as pl
from polars._typing import IntoExpr
from typing import Iterable

class Metrics(Handler):
    """Builds metrics for dataset"""
    def process(self, model: MenuModel, view: MenuView) -> None:
        title="Building Metrics >"
        print(title + view.line_break()[len(title):])
        
        print(">>> Aggregating metrics per developer...")
        df_per_dev=model.data["data_frames"]["exploded"] \
            .group_by(["developer", "year_month"]) \
            .agg([
                self.total_issues(),
                self.story_points(),
                self.time_tracking(),
                self.enhancements(),
                self.bugs(),
                self.spikes(),
                self.defects(),
                *self.other_labels(model),
            ]) \
            .with_columns(
                pl.col("time_tracking").map_elements(self.format_time_tracking, return_dtype=pl.String)
            ) \
            .sort(["developer", "year_month"])
        model.data["data_frames"]["df_per_dev"]=df_per_dev
        print(">>> total issues...")
        time.sleep(1)
        print(">>> story points...")
        time.sleep(1)
        print(">>> time tracking...")
        time.sleep(1.5)
        print(">>> enhancements, defects, bugs, and spikes...")
        time.sleep(1)
        print(f">>> {model.data["labels"]}...")
        time.sleep(1.5)
        
        print(">>> Aggregating metrics for primary developer...")
        
        df_per_primary_dev=model.data["data_frames"]["filtered"] \
            .group_by(["primary_developer", "year_month"]) \
            .agg([
                pl.col("time_tracking"),
                self.total_issues(),
                self.tracking_deficit(),
            ]) \
            .rename({"primary_developer": "developer"}) \
            .sort(["developer", "year_month"]) 
        model.data["data_frames"]["df_per_primary_dev"]=df_per_primary_dev
        
        time.sleep(1.5)
        
        print(">>> Joining results...")
        time.sleep(1.5)
        df_result=df_per_dev.join(
            df_per_primary_dev.select(["developer", "no_tracking_deficit"]),
            on="developer",
            how="left"
        ).with_columns(
            pl.col("no_tracking_deficit").fill_null(0.000).cast(pl.Float64)
        )
        
        model.data["data_frames"]["result"]=df_result
        print(Ansi.GREEN+"Complete  ✅\n"+Ansi.RESET)
        
        
    def total_issues(self) -> IntoExpr:
        return pl.len().alias("total_issues")
    
    def story_points(self) -> IntoExpr:
        return pl.col("story_points").sum().alias("story_point_sum")
    
    def time_tracking(self) -> IntoExpr:
        return pl.col("time_tracking").sum().alias("time_tracking")
    
    def enhancements(self) -> IntoExpr:
        return pl.col("is_enhancement").sum().alias("total_enhancements")
    
    def bugs(self) -> IntoExpr:
        return pl.col("is_bug").sum().alias("total_bugs")
    
    def spikes(self) -> IntoExpr:
        return pl.col("is_spike").sum().alias("total_spikes")
    
    def defects(self) -> IntoExpr:
        return pl.col("is_defect").sum().alias("total_defects")
    
    def other_labels(self, model) -> Iterable[IntoExpr]:
        return [pl.col(f"is_{label}").sum().alias(label) for label in model.data["labels"]]
    
    def format_time_tracking(self, s: str):
        weeks,r=divmod(int(s),604_800)
        days,r=divmod(r,86_400)
        hours,r=divmod(r,3_600)
        mins,r=divmod(r,60)
        secs,_=divmod(r*1000, 1000)
        return f"{weeks}w {days}d {hours}h {mins}m {secs}s"
    
    def tracking_deficit(self) -> IntoExpr:
        return (pl.col("time_tracking").filter(pl.col("time_tracking").is_null() | (pl.col("time_tracking")==0)).count() / pl.len() * 100).round(3).alias("no_tracking_deficit")
            