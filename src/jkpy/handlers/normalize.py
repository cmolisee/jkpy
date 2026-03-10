from __future__ import annotations
from jkpy.handlers.handler import Handler
import polars as pl
from jkpy.utils import Ansi
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView
import time
from datetime import datetime
from typing import List

class Normalize(Handler):
    """Normalizes and cleans the raw data to make it easier to work with"""
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
            
            dt=self.get_valid_done_date(model, issue["changelog"])
            if dt:
                year_month=dt.replace(tzinfo=None).strftime("%Y-%m")
            else:
                year_month=None
                
            row["year_month"]=year_month
            
            row["primary_developer"]=None if not fields.get("customfield_10264", {}) else fields.get("customfield_10264", {}).get("displayName", None)
            
            row["team"]=None if not fields.get("customfield_10235", {}) else fields.get("customfield_10235", {}).get("value", None)
            row["story_points"]=fields.get("customfield_10028", 0)
            row["time_tracking"]=fields.get("timespent", None)
            
            row["is_enhancement"]="enhancement" in [item.lower() for item in row["labels"]]
            row["is_bug"]="bug" in [item.lower() for item in row["labels"]]
            row["is_defect"]="defect" in [item.lower() for item in row["labels"]]
            row["is_spike"]="spike" in [item.lower() for item in row["labels"]]
            
            for label in model.data["labels"]:
                # WARNING: this is case sensitive
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
        
    def get_valid_done_date(self, model: MenuModel, changelog: List[object]) -> None|datetime:
        """
        Searches changelog with the following criteria:
            1. find the last block of status changes such that no status change
            to an invalid status has occured.
            2. find the earliest status change within that block of dates.
            
        if no valid status change blocks occurred at all or if no valid status changes 
        occured within the date range - return None.
        Otherwise, return the earliest valid status change date.

        :param model: model object with configs
        :type model: MenuModel
        :param changelog: changelog - array of history events for the given issue
        :type changelog: List[object]
        :return: valid earliest date or None
        :rtype: None|datetime
        """
        transitions=[]
        
        for history in changelog["histories"]:
            for item in history["items"]:
                if item["field"]=="status":
                    transitions.append({
                        "date": datetime.fromisoformat(history["created"]).replace(tzinfo=None),
                        "to_category": item["toString"].lower()
                    })
                    
        transitions.sort(key=lambda x: x["date"])
        
        # walk backwards to find a list of the last consecutive valid transitions
        # ignore instances of going in and out of valid statuses
        valid_dates=[]
        for t in reversed(transitions):
            if t["to_category"].lower() in [s.lower().replace("\"","") for s in model.data["statuses"]]:
                valid_dates.append(t["date"])
            else:
                break # anything before this is not applicable    
        
        if not valid_dates:
            return None
        
        # block is reveresed so re-reverse to get it in order
        for d in reversed(valid_dates):
            # all dates should be yyyy-mm-dd
            if model.data["start"] <= d <= model.data["end"]:
                return d
                   
        return None