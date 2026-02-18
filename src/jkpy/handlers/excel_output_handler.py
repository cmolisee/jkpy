from __future__ import annotations
from jkpy.handlers.handler import Handler
import os
from pathlib import Path
from datetime import datetime
import xlsxwriter
import polars as pl
from jkpy.utils import Print

class ExcelOutputHandler(Handler):
    def process(self, model: 'AppModel', view: 'AppView') -> None:
        view.print_terminal("Formatting and saving data...\n", Print.GREEN)
        output_path=os.path.join(
            Path.home(),
            model.data["path"],
            datetime.now().strftime("%Y%m%d_%H%M%S") + ".xlsx"
        )
        
        df_original=model.data["originaldata"]
        df_output=model.data["tempdata"][-1]
        
        with xlsxwriter.Workbook(output_path) as workbook:
            df_original.write_excel(workbook=workbook, worksheet="Raw Dataset")
            
            for idx, df in enumerate(df_output):
                if isinstance(df, pl.DataFrame):
                    df.write_excel(workbook=workbook, worksheet=f"dataset-{idx}")
        
        view.print_terminal("Data formatted and saved\n", Print.GREEN)
        view.print_terminal("see output at: {output_path}\n", Print.GREEN)