from __future__ import annotations
from jkpy.handlers.handler import Handler
import os
from pathlib import Path
from datetime import datetime
from typing import List
import xlsxwriter
from jkpy.utils import Ansi
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView
import time
import sys
from jkpy.utils import ProgressBar
import asyncio
import polars as pl

class ExcelOutputHandler(Handler):
    """Exports results to .xslx"""
    def process(self, model: MenuModel, view: MenuView) -> None:
        title="Formatting and saving data >"
        print(title + view.line_break()[len(title):])
        
        output_path=Path(os.path.expanduser(model.data["path"]),datetime.now().strftime("%Y%m%d_%H%M%S") + ".xlsx")
        os.makedirs(output_path.parent, exist_ok=True)
        print(f">>> Building output directory and file: {output_path}")
        time.sleep(1.5)
        
        print(">>> Gathering data...")
        time.sleep(1.5)

        errors=asyncio.run(self.export_data(model, output_path, view))
        print()

        for err in errors:
            print(err)

        print(Ansi.GREEN+f"Exported successfuly to {output_path} ✅\n"+Ansi.RESET)
        print()

    async def async_process(self, model, path):
        """Writes data to workbook"""
        errors: List[str]=[]
        with xlsxwriter.Workbook(path) as workbook:
            try:
                model.data["df_issues"].write_excel(workbook=workbook, worksheet=f"raw data")
            except Exception as e:
                errors.append(f"{Ansi.YELLOW}>>> {e}{Ansi.RESET}")
            
            for df in model.data["data_frames"]["result"].sort(["year_month", "developer"]).partition_by("year_month"):
                year_month=df.select(pl.col("year_month").first()).item()
                month_name=datetime.strptime(year_month, "%Y-%m").strftime("%B")
                try:
                    df.write_excel(workbook=workbook, worksheet=month_name)
                except Exception as e:
                    errors.append(f"{Ansi.YELLOW}>>> {e}{Ansi.RESET}")

        return errors
    
    async def export_data(self, model, path, view) -> List[str]:
        txt=">>> Exporting Data... "
        sys.stdout.write(txt)
        return await ProgressBar(min(40, view._width()), len(txt)).run_with(
            self.async_process(model, path)
        )