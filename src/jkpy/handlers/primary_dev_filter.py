from __future__ import annotations
from jkpy.handlers.handler import Handler
import polars as pl
from jkpy.utils import Print

class PrimaryDevFilter(Handler):
    def process(self, model: 'AppModel', view: 'AppView') -> None:
        title="Filtering data >"
        print(title + view.line_break()[len(title):])
        
        print(">>> Dropping issues without primary developer...")
        df=model.data["tempdata"][-1].filter(pl.col("primary_developer").is_not_null())
        model.data["tempdata"].append(df)
        
        Print.green(">>> Data has been filtered\n")