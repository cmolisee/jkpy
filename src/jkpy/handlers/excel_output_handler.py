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
        title="Formatting and saving data >"
        print(title + view.line_break()[len(title):])
        
        output_path=os.path.join(
            Path.home(),
            model.data["path"],
            datetime.now().strftime("%Y%m%d_%H%M%S") + ".xlsx"
        )
        
        df_original=model.data["originaldata"]
        df_output=model.data["tempdata"][-1]
        print(">>> Getting output path...")
        print(">>> Gathering data...")
        print(">>> Exporting data...")
        with xlsxwriter.Workbook(output_path) as workbook:
            df_original.write_excel(workbook=workbook, worksheet="Raw Dataset")
            
            for idx, df in enumerate(df_output):
                if isinstance(df, pl.DataFrame):
                    df.write_excel(workbook=workbook, worksheet=f"dataset-{idx}")
        
        Print.green(">>> Data exported successfuly")
        Print.green(">>> see output at: {output_path}\n")