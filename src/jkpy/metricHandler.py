from jkpy.jiraHandler import JiraHandler
from jkpy.utils import convert_seconds, has_duplicate, sys_exit
import pandas as pd
import numpy as np
import traceback

class MetricHandler(JiraHandler):
    """Builds metrics based on issue datasets.

    Args:
        JiraHandler (_type_): _description_
    """

    def handle(self, request):
        """Handler implementation.

        Args:
            request (_type_): _description_

        Returns:
            _type_: _description_
        """

        request.log("MetricHandler().handle().")
        if not request.proceed:
            sys_exit(0, request, "request.proceed is False. Exiting.")

        if not request.responseList:
            sys_exit(1, request, "request.responseList DNE.")

        metricsList=[]
        fullDataset=[]
        try:
            for responseObject in request.responseList:
                metrics={}
                month=responseObject.get("month");
                isQuarter=True if month in ["March", "June", "September", "December"] else False
                df=pd.json_normalize(responseObject.get("issues", []))
                dfs=df.shape[0]
                
                request.log(f"building metrics for {month}")
                metrics["overall"]=self.get_dataset_stats(df, month, "quarter" if isQuarter else "month", request);

                for n in request.nameLabels:
                    request.log(f"building metrics for name label {n} in {month}")

                    if dfs == 0:
                        metrics[n]={}
                        continue

                    nameSubset=df[df["fields.labels"].apply(lambda x: n in x)]
                    metrics[n]=self.get_dataset_stats(nameSubset, n, "name", request)

                for t in request.teamLabels:
                    request.log(f"building metrics for team label {t} in {month}")

                    if dfs == 0:
                        metrics[t]={}
                        continue

                    teamSubset=df[df["fields.customfield_10235.value"].apply(lambda x: x == t)]
                    metrics[t]=self.get_dataset_stats(teamSubset, t, "team", request)
                
                
                metricsList.append({
                    "set": month,
                    "data": metrics
                })
                fullDataset.extend(responseObject.get("issues", []))

            keys=list(map(lambda obj: obj.get("fields").get("key"), fullDataset))
            duplicates=has_duplicate(keys)
            if len(duplicates) > 0:
                print(f"WARNING: There are duplicates in the dataset: {", ".join(duplicates)}")
                request.log(f"There are duplicates in the dataset: {", ".join(duplicates)}")

            fullDatasetMetrics={}
            df=pd.json_normalize(fullDataset);
            dfs=df.shape[0]
        
            request.log(f"building metrics for full dataset")
            fullDatasetMetrics["overall"]=self.get_dataset_stats(df, "annual", "annual", request);
            
            for n in request.nameLabels:
                request.log(f"building annual metrics for name label {n}")

                if dfs == 0:
                    fullDatasetMetrics[n]={}
                    continue
                
                nameSubset=df[df["fields.labels"].apply(lambda x: n in x)]
                fullDatasetMetrics[n]=self.get_dataset_stats(nameSubset, n, "name", request)

            for t in request.teamLabels:
                request.log(f"building annual metrics for team label {t}")

                if dfs == 0:
                    fullDatasetMetrics[t]={}
                    continue

                teamSubset=df[df["fields.customfield_10235.value"].apply(lambda x: x == t)]
                fullDatasetMetrics[t]=self.get_dataset_stats(teamSubset, t, "team", request)

            metricsList.append({
                "set": "annual",
                "data": fullDatasetMetrics
            })

        except Exception:
            sys_exit(1, request, f"exception occured building metrics from response data: {traceback.format_exc()}")

        request.fullDataset=fullDataset
        request.metricsList=metricsList
        return super().handle(request)

    def get_dataset_stats(self, dataset: pd.DataFrame, datasetName: str, datasetType: str, request):
        """Parses the dataset using the provided arguments to produce metrics.

        Args:
            dataset (pd.DataFrame): _description_
            datasetName (str): _description_
            datasetType (str): _description_
            request (_type_): _description_

        Returns:
            _type_: _description_
        """
        stats={
            "datasetName": datasetName,
            "totalIssues": dataset.shape[0],
        }

        if stats.get("totalIssues") > 0:
            primaryDevDf=dataset
            if datasetType == "name":
                displayName=datasetName.replace("-", " ")
                
                primaryDevDf=dataset[dataset["fields.customfield_10264"].apply(lambda x: 
                    pd.isna(x) or x == '' or (displayName in x)
                )]

            stats["storyPointSum"]=dataset["fields.customfield_10028"].sum()
            stats["totalTimeSpent"]=convert_seconds(seconds=dataset["fields.timespent"].sum())
            stats["totalNoTracking"]=dataset["fields.timespent"].isna().sum()
            stats["totalEnhancement"]=dataset[dataset["fields.labels"].apply(lambda x: "Enhancement" in x)].shape[0]
            stats["totalBugs"]=dataset[dataset["fields.labels"].apply(lambda x: "Bug" in x)].shape[0]
            stats["totalDefects"]=dataset[dataset["fields.labels"].apply(lambda x: "Defect" in x)].shape[0]
            stats["totalSpikes"]=dataset[dataset["fields.labels"].apply(lambda x: "Spike" in x)].shape[0]
            # extra metrics
            stats["totalOnePointers"]=dataset["fields.customfield_10028"].apply(lambda x: x == 1).sum()
            stats["totalTwoPointers"]=dataset["fields.customfield_10028"].apply(lambda x: x == 2).sum()
            stats["totalThreePointers"]=dataset["fields.customfield_10028"].apply(lambda x: x == 3).sum()
            stats["totalFivePointers"]=dataset["fields.customfield_10028"].apply(lambda x: x == 5).sum()
            # calculated
            stats["storyPointAverage"]=round(dataset["fields.customfield_10028"].mean())
            stats["noTrackingDeficit"]=round((stats.get("totalNoTracking") / stats.get("totalIssues")) * 100, 3)
            # metrics by labels
            for metricLabel in request.metricLabels:
                if primaryDevDf.empty:
                    stats[metricLabel]=0
                else:
                    stats[metricLabel]=primaryDevDf[primaryDevDf["fields.labels"].apply(lambda x: metricLabel in x)].shape[0]
            # run additional stats if nameLabels exists
            # primarily for quarterly and annual metrics
            if datasetType == "quarter" or datasetType == "annual":
                stats["noStoryPoints"]=dataset["fields.customfield_10028"].apply(lambda x: x is None or x == 0).sum()
                stats["noNameLabel"]=dataset["fields.customfield_10235.value"].apply(lambda x: any(str(x) in n for n in request.nameLabels)).sum()
    
        return stats
