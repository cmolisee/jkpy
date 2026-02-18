from __future__ import annotations
from jkpy.handlers.handler import Handler
import polars as pl
from jkpy.utils import Print

class PreprocessingTeamLabelsHandler(Handler):
    def process(self, model: 'AppModel', view: 'AppView') -> None:
        view.print_terminal("Preprocessing team and labels columns...\n", Print.GREEN)
        
        df=model.data["tempdata"][-1]
        df=df.with_columns(
            pl.concat_list("fields.customfield_10235.value", "fields.labels").alias("team_and_labels")
        )
        model.data["tempdata"].append(df)
        
        view.print_terminal("fields.customfield_10235.value and fields.labels fully processed\n", Print.GREEN)
        view.print_terminal("team_and_labels column added\n", Print.GREEN)
