from __future__ import annotations
from jkpy.handlers.handler import Handler
import polars as pl
from jkpy.utils import Print

class PreprocessingDateHandler(Handler):
    def process(self, model: 'AppModel', view: 'AppView') -> None:
        view.print_terminal("Preprocessing statuscategorychangedate column...\n", Print.GREEN)
        df=model.data["tempdata"][-1]
        df=df.with_columns(
            pl.col("fields.statuscategorychangedate").cast(pl.Datetime).alias("category_change_date")
        )
        df=df.with_columns(
            pl.col("category_change_date").dt.month().alias("category_change_month"),
            pl.col("category_change_date").dt.year().alias("category_change_year")
        )
        model.data["tempdata"].append(df)
        
        view.print_terminal("statuscategorychangedate fully processed\n", Print.GREEN)
        view.print_terminal("category_change_date column added\n", Print.GREEN)
