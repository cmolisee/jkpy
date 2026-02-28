from __future__ import annotations
from jkpy.handlers.handler import Handler
import polars as pl
from jkpy.utils import Ansi
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView
import time

class PreprocessingDevLabelHandler(Handler):
    def process(self, model: MenuModel, view: MenuView) -> None:
        title="Preprocessing team and labels columns >"
        print(title + view.line_break()[len(title):])
        
        print(">>> Processing labels to developer_labels...")
        df=model.data["tempdata"][-1]
        df=df.with_columns(
            pl.col("fields.labels").list.set_intersection(model.data["members"]).alias("developer_labels")
            # pl.concat_list("fields.customfield_10235.value", "fields.labels").alias("team_and_labels")
        )
        model.data["tempdata"].append(df)
        time.sleep(1.5)
        
        print(Ansi.GREEN+"Labels column processed to developer_labels  ✅\n"+Ansi.RESET)
