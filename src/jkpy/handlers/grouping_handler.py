from __future__ import annotations
from jkpy.handlers.handler import Handler
from jkpy.utils import Print

class GroupingHandler(Handler):
    def process(self, model: 'AppModel', view: 'AppView') -> None:
        title="Grouping data >"
        print(title + view.line_break()[len(title):])
        
        print(">>> Grouping by month...")
        print(">>> Grouping by year...")
        print(">>> Grouping by teams...")
        print(">>> Grouping by labels...")
        df=model.data["tempdata"][-1].group_by("category_change_month","category_change_year","team_and_labels")
        model.data["tempdata"].append(df)
        
        Print.green(">>> Data grouping complete\n")