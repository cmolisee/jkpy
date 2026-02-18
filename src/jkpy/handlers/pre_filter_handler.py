from __future__ import annotations
from jkpy.handlers.handler import Handler
import polars as pl
from jkpy.utils import Print

class PreFilterHandler(Handler):
    def process(self, model: 'AppModel', view: 'AppView') -> None:
        view.print_terminal("Filtering data...\n", Print.GREEN)
        df=model.data["tempdata"][-1].filter(
            pl.col("fields.statuscategorychangedate").cast(pl.Datetime) <= pl.col("fields.resolutiondate").cast(pl.Datetime),
            (pl.col("fields.labels").list.set_intersection(model.data["members"]).list.len() != 0) | pl.col("fields.customfield_10235.value").is_in(model.data["teams"])
        )
        model.data["tempdata"].append(df)
        
        view.print_terminal("Data has been filtered\n", Print.GREEN)