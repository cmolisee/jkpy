from datetime import date
from datetime import datetime
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)
class Ansi:
    # https://talyian.github.io/ansicolors/
    RED="\x1b[31m"
    GREEN="\x1b[32m"
    YELLOW="\x1b[33m"
    CYAN="\x1b[36m"
    MAGENTA="\x1b[35m"
    
    BOLD="\x1b[1m"
    RESET="\x1b[0m"
    
    @staticmethod
    def up(y):
        """Move cursor up 'y' lines, to beginning of line"""
        return f"\x1b[{y}F"
    
    @staticmethod
    def right(x):
        """Move cursor right 'x' columns"""
        return f"\x1b[{x}C"
    
    @staticmethod
    def overwrite():
        """Overwrite all text from cursor, for the next n bits of output"""
        return "\x1b[K"
    
    @staticmethod
    def erase_line():
        """Erase the entire current line"""
        return f"\x1b[2K"