from __future__ import annotations
from jkpy.handlers.handler import Handler
import polars as pl
from jkpy.utils import Ansi
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView
import time

class Filter(Handler):
    def process(self, model: MenuModel, view: MenuView) -> None:
        title="Filtering data >"
        print(title + view.line_break()[len(title):])
        
        print(">>> Dropping unresolved issues...")
        time.sleep(1.5)
        print(">>> Dropping issues without primary developer...")
        time.sleep(1.5)
        
        df_filtered=model.data["data_frames"]["normalized"].filter(
            pl.col("primary_developer").is_not_null(),
            pl.col("green_status")==True
        )
        
        print(">>> Exploding developers into developer rows...")
        df_exploded=df_filtered.explode("developers").rename({"developers": "developer"})
        
        model.data["data_frames"]["filtered"]=df_filtered
        model.data["data_frames"]["exploded"]=df_exploded
        
        print(Ansi.GREEN+"Data has been filtered ✅\n"+Ansi.RESET)