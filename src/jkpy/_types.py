from typing import TypedDict
from typing import Optional
from typing import List
from typing import Any
from typing import Set
from typing import Tuple
from polars.dataframe.frame import DataFrame

class Configurations(TypedDict):
    email: Optional[str]
    token: Optional[str]
    path: Optional[str]
    members: Optional[List[str]]
    teams: Optional[List[str]]
    statuses: Optional[List[str]]
    labels: Optional[List[str]]
    ignore_labels: Optional[List[str]]
    host: Optional[str]

class RuntimeData(TypedDict):
    originaldata: Optional[DataFrame]
    tempdata: Optional[List[Any]]
    accounts: Optional[Set[Tuple[Any, ...]]]
    start: Optional[str]
    end: Optional[str]
    
class MenuData(Configurations, RuntimeData):
    pass