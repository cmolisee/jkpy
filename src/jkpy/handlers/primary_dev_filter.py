from __future__ import annotations
from jkpy.handlers.handler import Handler
import polars as pl
from jkpy.utils import Ansi
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView
import time

class PrimaryDevFilter(Handler):
    def process(self, model: MenuModel, view: MenuView) -> None:
        title="Filtering data >"
        print(title + view.line_break()[len(title):])
        
        print(">>> Dropping issues without primary developer...")
        df=model.data["tempdata"][-1].filter(pl.col("primary_developer").is_not_null())
        model.data["tempdata"].append(df)
        time.sleep(1.5)
        
        print(Ansi.GREEN+"Data has been filtered  ✅\n"+Ansi.RESET)