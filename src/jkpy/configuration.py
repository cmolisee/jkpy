import os
import json
from datetime import date
from datetime import datetime
from pathlib import Path
from typing import TypedDict
from typing import Optional
from typing import List
from typing import Set
from typing import Tuple
from typing import Any
import polars as pl
from jkpy.utils import DateTimeEncoder

class ApplicationConfigurationType(TypedDict):
    email: Optional[str]
    token: Optional[str]
    path: Optional[str]
    members: Optional[List[str]]
    teams: Optional[List[str]]
    statuses: Optional[List[str]]
    labels: Optional[List[str]]
    host: Optional[str]
    handlers: Optional[List[str]]
    
class ApplicationRuntimeConfigurationType(TypedDict):
    original_data: Optional[pl.DataFrame]
    # queue of each step of the manipulated/transformed original_data
    temp_data: Optional[List[Any]]

class ApplicationCachedType(TypedDict):
    accounts: Optional[Set[Tuple[Any, ...]]]
    start: Optional[str]
    end: Optional[str]
    
class ConfigurationType(ApplicationConfigurationType,ApplicationRuntimeConfigurationType,ApplicationCachedType):
    """
    Type hint for Configuration
    """
    pass

class Configuration:
    @classmethod
    def get_config(self) -> ConfigurationType:
        home_dir=Path.home()
        relative_path="Documents/.jkpy/config.txt"
        full_path=Path(os.path.join(home_dir, relative_path))
        
        if not full_path.exists():
            default_config: Configuration=dict.fromkeys(Configuration.__annotations__.keys(), None)
                
            with Path(full_path).open('w', encoding='utf-8') as f:
                json.dump(default_config, f, cls=DateTimeEncoder)
                
        with full_path.open("r") as f:
            data=f.read()
        
        return json.loads(data) if data else {}
    
    @classmethod
    def set_config(self, request: ConfigurationType) -> ConfigurationType:
        application_configuration: Configuration=self.get_config()
        
        for key, value in request.items():
            if value is None:
                continue
            if key=="path":
                Path(value).mkdir(parents=True, exist_ok=True)
                application_configuration[key]=value
                
            elif key in ["members","teams","statuses","labels"]:
                application_configuration[key]=value
            elif key=="start":
                try:
                    application_configuration[key]=datetime.strptime(value, '%Y-%m-%d')
                except:
                    application_configuration[key]=date(date.today().year, 1, 1).isoformat()
            elif key=="end":
                try:
                    application_configuration[key]=datetime.strptime(value, '%Y-%m-%d')
                except:
                    application_configuration[key]=date.today().strftime("%Y-%m-%d")
            elif key in ["remove_members","remove_teams","remove_statuses","remove_labels"]:
                application_configuration_key=key.replace("remove_", "")
                application_configuration_list=application_configuration[application_configuration_key]
                
                updated_list=[item for item in application_configuration_list if item not in value]
                application_configuration[application_configuration_key]=sorted(updated_list)
            elif key in ConfigurationType.__annotations__.keys():
                application_configuration[key]=value
            else:
                print(f"\"{key}\" ignored")

        home_dir=Path.home()
        relative_path="Documents/.jkpy/config.txt"
        full_path=Path(os.path.join(home_dir, relative_path))
        with Path(full_path).open('w', encoding='utf-8') as f:
                json.dump(application_configuration, f, cls=DateTimeEncoder)
            
        return application_configuration