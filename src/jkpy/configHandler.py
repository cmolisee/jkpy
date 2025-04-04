from jkpy.jiraHandler import JiraHandler
from jkpy.utils import clean_folder_path, sys_exit
from pathlib import Path
from typing import Dict
import json
import os

class ConfigHandler(JiraHandler):
    """Parses and updates configuration options.

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

        request.log("ConfigHandler().handle().")
        
        if not request.proceed:
            sys_exit(0, request, "request.proceed is False. Exiting.")
        
        config: Dict[str, any]=self.get_config(request)
        
        if request.showConfig:
            print(json.dumps(config, indent=4, sort_keys=True))
            sys_exit(0, request, "show configs only.")

        if request.email:
            request.log(f"updating email from {config["email"]} to {request.email}")
            config["email"]=request.email
        else:
            request.email=config.get("email", "")

        if request.token:
            request.log(f"updating token from {config["token"]} to {request.token}")
            config["token"]=request.token
        else:
            request.token=config.get("token", "")

        if request.folderPath:
            request.log(f"updating and creating folderPath from {config["folderPath"]} to {request.folderPath}")
            cleanPath=clean_folder_path(request.folderPath) # clean and get folderPath as PosixPath
            cleanPath.mkdir(parents=True, exist_ok=True) # make folder as needed
            config["folderPath"]=str(cleanPath) # convert path to string to store in config
        else:
            request.folderPath=config.get("folderPath", os.path.join(Path.home(), "Desktop"))

        if request.teamLabels and len(request.teamLabels) > 0:
            request.log(f"adding and sorting team labels {", ".join(request.teamLabels)}.")
            teamLabelsSet=set(config.get("teamLabels", [])) # get existing config as a set
            teamLabelsSet.update(sorted(request.teamLabels.split(","))) # update set with values from request
            config["teamLabels"]=list(teamLabelsSet) # set config
            request.teamLabels=list(teamLabelsSet) # set reqeust
        else:
            request.teamLabels=sorted(config.get("teamLabels", []))

        if request.nameLabels and len(request.nameLabels) > 0:
            request.log(f"adding and sorting name labels {", ".join(request.nameLabels)}.")
            nameLabelsSet=set(config.get("nameLabels", [])) # get existing config as a set
            nameLabelsSet.update(sorted(request.nameLabels.split(","))) # update set with values from request
            config["nameLabels"]=list(nameLabelsSet) # set config
            request.nameLabels=list(nameLabelsSet) # set reqeust
        else:
            request.nameLabels=sorted(config.get("nameLabels", []))

        if request.statusTypes and len(request.statusTypes) > 0:
            request.log(f"adding status types {", ".join(request.statusTypes)}.")
            statusTypesSet=set(config.get("statusTypes", [])) # get existing config as a set
            statusTypesSet.update(request.statusTypes.split(",")) # update set with values from request
            config["statusTypes"]=list(statusTypesSet) # set config
            request.statusTypes=list(statusTypesSet) # set reqeust
        else:
            request.statusTypes=config.get("statusTypes", [])

        if request.metricLabels and len(request.metricLabels) > 0:
            request.log(f"adding metric labels {", ".join(request.metricLabels)}.")
            metricLabelsSet=set(config.get("metricLabels", [])) # get existing config as a set
            metricLabelsSet.update(request.metricLabels.split(",")) # update set with values from request
            config["metricLabels"]=list(metricLabelsSet) # set config
            request.metricLabels=list(metricLabelsSet) # set reqeust
        else:
            request.metricLabels=config.get("metricLabels", [])

        if request.remove_teamLabels and len(request.remove_teamLabels) > 0:
            request.log(f"removing team labels {", ".join(request.remove_teamLabels)}.")
            teamLabelsList=config.get("teamLabels", []) # updated labels are in the config
            # filter out all items to remove into a new list
            updatedTeamLabels=[label for label in teamLabelsList if label not in request.remove_teamLabels.split(",")]
            config["teamLabels"]=sorted(updatedTeamLabels) # update config
            request.teamLabels=sorted(updatedTeamLabels) # update request

        if request.remove_nameLabels and len(request.remove_nameLabels) > 0:
            request.log(f"removing name labels {", ".join(request.remove_nameLabels)}.")
            nameLabelsArray=config.get("nameLabels", []) # updated labels are in the config
            # filter out all items to remove into a new list
            updatedNameLabels=[label for label in nameLabelsArray if label not in request.remove_nameLabels.split(",")]
            config["nameLabels"]=sorted(updatedNameLabels) # update config
            request.nameLabels=sorted(updatedNameLabels) # update request

        if request.remove_statusTypes and len(request.remove_statusTypes) > 0:
            request.log(f"removing status types {", ".join(request.remove_statusTypes)}.")
            statusTypesArray=config.get("statusTypes", []) # updated labels are in the config
            # filter out all items to remove into a new list
            updatedStatusTypes=[status for status in statusTypesArray if status not in request.remove_statusTypes.split(",")]
            config["statusTypes"]=updatedStatusTypes # update config
            request.statusTypes=updatedStatusTypes # update request

        if request.remove_metricLabels and len(request.remove_metricLabels) > 0:
            request.log(f"removing metric labels {", ".join(request.remove_metricLabels)}.")
            metricLabelsArray=config.get("metricLabels", []) # updated labels are in the config
            # filter out all items to remove into a new list
            updatedMetricLabels=[label for label in metricLabelsArray if label not in request.remove_metricLabels.split(",")]
            config["metricLabels"]=updatedMetricLabels # update config
            request.metricLabels=updatedMetricLabels # update request

        self.write_update_config(config, request)
        if request.isSetup:
            sys_exit(0, request, "config setup only.")

        return super().handle(request)
    
    def get_config(self, request):
        """Retrieves configuration from file if it exists.

        Args:
            request (_type_): _description_

        Returns:
            _type_: _description_
        """
        configPath=Path(os.path.join(Path.home(), "Documents/.jkpy/config.txt"))
        configPath.parent.mkdir(parents=True, exist_ok=True)
        
        if not configPath.exists():
            request.log(f"config file did not exist. creating new config at {configPath}.")
            configPath.touch()
        
        try:
            with configPath.open("r") as f:
                data=f.read()
           
            return {} if data == "" else json.loads(data)
        except Exception as e:
            sys_exit(1, request, f"exception occured attempting to open and READ the config file: {e}")
    
    def write_update_config(self, config, request):
        """Writes configurations to file. This will create a file if it DNE. This will override the existing file.

        Args:
            config (_type_): _description_
            request (_type_): _description_
        """
        configPath=Path(os.path.join(Path.home(), "Documents/.jkpy/config.txt"))
        configPath.parent.mkdir(parents=True, exist_ok=True)
        
        if not configPath.exists():
            request.log(f"config file did not exist. creating new config at {configPath}.")
            configPath.touch()
        
        try:
            with configPath.open("w") as f:
                f.write(json.dumps(config))
        except Exception as e:
            sys_exit(1, request, f"exception occured attempting to open and WRITE the config file: {e}")
