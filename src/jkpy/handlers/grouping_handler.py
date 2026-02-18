from __future__ import annotations
from jkpy.handlers.handler import Handler
from jkpy.utils import Print

class GroupingHandler(Handler):
    def process(self, model: 'AppModel', view: 'AppView') -> None:
        view.print_terminal("Grouping data...\n", Print.GREEN)
        
        df=model.data["tempdata"][-1].group_by("category_change_month","category_change_year","team_and_labels")
        model.data["tempdata"].append(df)
        
        view.print_terminal("Data grouping complete\n", Print.GREEN)