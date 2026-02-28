from __future__ import annotations
from jkpy.handlers.handler import Handler
import polars as pl
from jkpy.utils import Ansi
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView
import time
from datetime import datetime
from datetime import timedelta

class Normalize(Handler):
    def process(self, model: MenuModel, view: MenuView) -> None:
        title="Normalizing Data >"
        print(title + view.line_break()[len(title):])

        rows=[]
        for issue in model.data["raw_issues"]:
            row={}
            fields=issue["fields"]
            
            row["key"]=issue["key"]
            
            row["summary"]=fields.get("summary", "")
            row["labels"]=fields.get("labels",[]) or []
            row["developers"]=list(set(model.data["members"]) & set(row["labels"]))
            raw_date=fields.get("statuscategorychangedate")
            if raw_date:
                dt=datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                year_month=dt.strftime("%Y-%m")
            else:
                year_month=None
                
            row["year_month"]=year_month
            
            row["primary_developer"]=None if not fields.get("customfield_10264", {}) else fields.get("customfield_10264", {}).get("displayName", None)
            
            resolution_date=fields.get("resolutiondate", datetime.today().isoformat())
            change_date=fields.get("statuscategorychangedate", (datetime.today()-timedelta(days=1)).isoformat())
            row["green_status"]=datetime.fromisoformat(change_date).date()<=datetime.fromisoformat(resolution_date).date()
            
            row["team"]=None if not fields.get("customfield_10235", {}) else fields.get("customfield_10235", {}).get("value", None)
            row["story_points"]=fields.get("customfield_10028", 0)
            row["time_tracking"]=fields.get("timespent", None)
            
            row["is_enhancement"]="enhancement" in row["labels"]
            row["is_bug"]="bug" in row["labels"]
            row["is_defect"]="defect" in row["labels"]
            row["is_spike"]="spike" in row["labels"]
            
            for label in model.data["labels"]:
                row[f"is_{label}"]=label in row["labels"]
            
            rows.append(row)
                
        print(">>> Collecting labels...")
        time.sleep(0.3)
        print(">>> Parsing developers...")
        time.sleep(0.3)
        print(">>> Parsing dates...")
        time.sleep(0.3)
        print(">>> Locating primary developer...")
        time.sleep(0.3)
        print(">>> Determining green status...")
        time.sleep(0.3)
        print(">>> Parsing team name...")
        time.sleep(0.3)
        print(">>> Extracting story points...")
        time.sleep(0.3)
        print(">>> Translating timespent...")
        time.sleep(0.3)
        print(">>> Identifying labels...")
        time.sleep(0.3)
        
        model.data["data_frames"]["normalized"]=pl.DataFrame(rows)
        
        print(Ansi.GREEN+"Data has been filtered ✅\n"+Ansi.RESET)