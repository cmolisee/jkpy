from __future__ import annotations
from jkpy.handlers.handler import Handler
from jkpy.utils import Ansi
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView
import time

class GroupingHandler(Handler):
    def process(self, model: MenuModel, view: MenuView) -> None:
        title="Grouping data >"
        print(title + view.line_break()[len(title):])
        
        print(">>> Grouping by month...")
        time.sleep(1)
        print(">>> Grouping by developer...")
        time.sleep(1)
        # print(">>> Grouping by labels...")
        # time.sleep(1)
        
        df=model.data["tempdata"][-1].group_by("category_change_month", "developer_labels")
        model.data["tempdata"].append(df)
        
        print(Ansi.GREEN+"Data grouping complete  ✅"+Ansi.RESET)