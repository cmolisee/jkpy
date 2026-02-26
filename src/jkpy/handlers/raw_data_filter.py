from __future__ import annotations
from jkpy.handlers.handler import Handler
import polars as pl
from jkpy.utils import Ansi
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView
import time

class RawDataFilter(Handler):
    def process(self, model: MenuModel, view: MenuView) -> None:
        title="Filtering data >"
        print(title + view.line_break()[len(title):])
        
        print(">>> Dropping unresolved issues...")
        time.sleep(1.5)
        print(">>> Dropping issues without team or member...")
        time.sleep(1.5)
        
        df=model.data["tempdata"][-1].filter(
            pl.col("fields.statuscategorychangedate").cast(pl.Datetime) <= pl.col("fields.resolutiondate").cast(pl.Datetime),
            (pl.col("fields.labels").list.set_intersection(model.data["members"]).list.len() != 0) | pl.col("fields.customfield_10235.value").is_in(model.data["teams"])
        )
        model.data["tempdata"].append(df)
        
        print(Ansi.GREEN+"Data has been filtered ✅"+Ansi.RESET)