from datetime import date
from datetime import datetime
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

class Print:
    RED="\x1b[31m"
    GREEN="\x1b[32m"
    YELLOW="\x1b[33m"
    CYAN="\x1b[36m"
    MAGENTA="\x1b[35m"
    NC="\033[0m"
    
    def red(content):
        print(f"{Print.RED}{content}{Print.NC}")
    
    def green(content):
        print(f"{Print.GREEN}{content}{Print.NC}")
        
    def yellow(content):
        print(f"{Print.YELLOW}{content}{Print.NC}")
        
    def cyan(content):
        print(f"{Print.CYAN}{content}{Print.NC}")
        
    def magenta(content):
        print(f"{Print.MAGENTA}{content}{Print.NC}")