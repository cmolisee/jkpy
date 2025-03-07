from dataclasses import dataclass
from requests.auth import HTTPBasicAuth

@dataclass 
class QueryObject:
    jql: str
    fields: str
    
@dataclass
class RequestObject:
    month: str
    type: str
    method: str
    path: str
    headers: dict
    query: QueryObject
    auth: HTTPBasicAuth