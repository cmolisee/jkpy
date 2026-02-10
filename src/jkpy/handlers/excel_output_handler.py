from jkpy.handlers.base_handler import BaseHandler
from jkpy.configuration import ConfigurationType
import os
from pathlib import Path
from datetime import datetime
import xlsxwriter

class ExcelOutputHandler(BaseHandler):
    def handle(self, request: ConfigurationType) -> None:
        output_path=os.path.join(
            Path.home(),
            request["path"],
            datetime.now().strftime("%Y%m%d_%H%M%S") + ".xlsx"
        )
        df_original=request["original_data"]
        df_output=request["temp_data"][-1]
        
        with xlsxwriter.Workbook(output_path) as workbook:
            df_original.write_excel(workbook=workbook, worksheet="Raw Dataset")
            df_output.write_excel(workbook=workbook, worksheet="Metrics")
        
        return super().handle(request)