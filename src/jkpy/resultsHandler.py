"""jkpy resultsHandler"""
# jkpy/resultsHandler.py

from datetime import datetime
import os
from pathlib import Path
import pandas as pd

from jkpy.jiraHandler import JiraHandler
from jkpy.utils import sys_exit

class ResultsHandler(JiraHandler):
    """MetricHandler(JiraHandler)
    
    Concrete implementation of the JiraHandler interface.
    Responsible for building metrics from response objects.
    """

    def handle(self, request):
        """MetricHandler(JiraHandler).hanlde(self, request)
        
        Concrete implementation of the handle() method from JiraHandler.
        Handles the processing and output of all metrics.
        """

        request.log("ResultsHandler().handle().")
        if not request.proceed:
            sys_exit(0, request, "request.proceed is False. Exiting.")
        
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

        try:
            outputPath=os.path.join(Path.home(), request.folderPath, str(datetime.now().year) + "_kpis.xlsx")

            if request.startDate or request.endDate:
                outputPath=os.path.join(Path.home(), request.folderPath, "run_result" + ".xlsx")

            logPath=os.path.join(Path.home(), request.folderPath, "jkpy.logs.txt")

            # normalize issues structure for output to file
            df=pd.json_normalize(request.fullDataset)

            request.log(f"exporting results to {outputPath}")
            with pd.ExcelWriter(outputPath) as writer:
                # export dataset to output file on sheet=dataset
                df.to_excel(writer, sheet_name='data', index=False)

                for metrics in request.metricsList:
                    df2=pd.DataFrame.from_dict(metrics.get("data"), orient="index")
                    df2.to_excel(writer, sheet_name=metrics.get("set"), index=False)
                    # if df2.shape[0] > 0:
                    #     df2.to_excel(writer, sheet_name=metrics.get("set"), index=False)
                    # else:
                    #     pd.DataFrame().to_excel(writer, sheet_name=metrics.get("set"), index=False)

            with open(logPath, "a") as file:
                for log in request.logs:
                    file.write(log + "\n")
    
        except Exception as e:
            sys_exit(1, request, f"exception occured outputing results: {e}")

        return super().handle(request)