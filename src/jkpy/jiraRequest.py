from datetime import datetime

class JiraRequest:
    def __init__(self, requestConfig={}):
        """Initialize request object.
        This is the single source of truth for all data that is carried to all handlers.

        Args:
            requestConfig (dict, optional): _description_. Defaults to {}.
        """
        # user configs
        self.email=requestConfig.get("email", None)
        self.token=requestConfig.get("token", None)
        self.folderPath=requestConfig.get("folderPath", None)
        self.teamLabels=requestConfig.get("teamLabels", None)
        self.nameLabels=requestConfig.get("nameLabels", None)
        self.statusTypes=requestConfig.get("statusTypes", None)
        self.metricLabels=requestConfig.get("metricLabels", None)
        self.remove_teamLabels=requestConfig.get("remove_teamLabels", None)
        self.remove_nameLabels=requestConfig.get("remove_nameLabels", None)
        self.remove_statusTypes=requestConfig.get("remove_statusTypes", None)
        self.remove_metricLabels=requestConfig.get("remove_metricLabels", None)
        # flags
        self.showConfig=requestConfig.get("showConfig", False)
        self.isUpdate=requestConfig.get("update", True)
        self.isSetup=requestConfig.get("isSetup", False)
        # processing variables
        self.startDate=requestConfig.get("startDate", None)
        self.endDate=requestConfig.get("endDate", None)
        self.proceed=True
        self.logs=[]
        self.requestData=None
        self.responseData=None
        self.metrics=None
        self.timestamp=int(datetime.now().timestamp())

    def __str__(self):
        """Override to define how this class is converted to a string.
        """
        return f"""JiraRequest(
            email={self.email},
            token={self.token},
            folderPath={self.folderPath},
            teamLabels={self.teamLabels},
            nameLabels={self.nameLabels},
            statusTypes={self.statusTypes},
            metricLabels={self.metricLabels},
            remove_teamLabels={self.remove_teamLabels},
            remove_nameLabels={self.remove_nameLabels},
            remove_statusTypes={self.remove_statusTypes},
            remove_metricLabels={self.remove_statusTypes},
            startDate={self.startDate},
            endDate={self.endDate},
            isSetup={self.isSetup},
            proceed={self.proceed},
            logs={self.logs},
            requestData={self.requestData},
            responseData={self.responseData},
            metrics={self.metrics},
            timestamp={self.timestamp},
            showConfig={self.showConfig}
        )"""

    def log(self, log):
        """Logging function.

        Args:
            log (_type_): _description_
        """
        self.logs.append(f"[{self.timestamp}] {log}")