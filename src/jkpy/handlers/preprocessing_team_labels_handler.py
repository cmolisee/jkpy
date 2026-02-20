from __future__ import annotations
from jkpy.handlers.handler import Handler
import polars as pl
from jkpy.utils import Print

class PreprocessingTeamLabelsHandler(Handler):
    def process(self, model: 'AppModel', view: 'AppView') -> None:
        title="Preprocessing team and labels columns >"
        print(title + view.line_break()[len(title):])
        
        print(">>> Casting customfield_10235 and labels columns to team_and_labels...")
        df=model.data["tempdata"][-1]
        df=df.with_columns(
            pl.concat_list("fields.customfield_10235.value", "fields.labels").alias("team_and_labels")
        )
        model.data["tempdata"].append(df)
        
        Print.green(">>> Team and labels columns processed")
        Print.green(">>> team_and_labels\n")
