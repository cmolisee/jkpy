from __future__ import annotations
from jkpy.handlers.handler import Handler
import polars as pl
from jkpy.utils import Print

class PreprocessingDateHandler(Handler):
    def process(self, model: 'AppModel', view: 'AppView') -> None:
        title="Preprocessing statuscategorychangedate column >"
        print(title + view.line_break()[len(title):])
        
        print(">>> Resolving statuscategorychangedate column to category_change_date...")
        df=model.data["tempdata"][-1]
        df=df.with_columns(
            pl.col("fields.statuscategorychangedate").cast(pl.Datetime).alias("category_change_date")
        )
        print(">>> Resolving category_change_date column to category_change_month...")
        print(">>> Resolving category_change_date column to category_change_year...")
        df=df.with_columns(
            pl.col("category_change_date").dt.month().alias("category_change_month"),
            pl.col("category_change_date").dt.year().alias("category_change_year")
        )
        model.data["tempdata"].append(df)
        
        Print.green(">>> statuscategorychangedate processed")
        Print.green(">>> category_change_date, category_change_month, category_change_year\n")
