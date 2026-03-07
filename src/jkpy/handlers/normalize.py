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
            
            valid_done_date=self.get_valid_done_date(model, issue["changelog"])
            if valid_done_date:
                dt=datetime.fromisoformat(valid_done_date.replace("Z", "+00:00"))
                year_month=dt.strftime("%Y-%m")
            else:
                year_month=None
                
            row["year_month"]=year_month
            
            row["primary_developer"]=None if not fields.get("customfield_10264", {}) else fields.get("customfield_10264", {}).get("displayName", None)
            
            # resolution_date=fields.get("resolutiondate", datetime.today().isoformat())
            # change_date=fields.get("statuscategorychangedate", (datetime.today()-timedelta(days=1)).isoformat())
            # these should ALL be in a green status based on the query
            # row["green_status"]=datetime.fromisoformat(change_date).date()<=datetime.fromisoformat(resolution_date).date()
            
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
        
        # walk backwards to find the last consecutive valid transition block
        last_valid_block=[]
        for t in reversed(transitions):
            if t["to_category"] in model.data["statuses"]:
                last_valid_block=t["date"]
            else:
                break # anything before this is not applicable    
        
        if not last_valid_block:
            return None
        
        # block is reveresed so re-reverse to get it in order
        for t in list(reversed(last_valid_block)):
            # all dates should be yyyy-mm-dd
            if model.data["start"] <= t["date"] <= model.data["end"]:
                return t["date"]
                    
        return None