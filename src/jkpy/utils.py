from datetime import datetime
from pathlib import Path
import os
import sys

def clean_folder_path(path: str):
    """Removes the file name from the end of a path string if it exists.

    Args:
        path (str): _description_

    Returns:
        _type_: _description_
    """
    if os.path.isfile(path):
        return Path(os.path.dirname(path))
    else:
        return Path(path)

def sys_exit(code: int, request, log):
    """Abstracts the code to generate log on system exit.

    Args:
        code (int): _description_
        request (_type_): _description_
        log (_type_): _description_
    """
    if request:
        logPath=os.path.join(Path.home(), request.folderPath if request.folderPath else "Desktop/jkpy", "jkpy.logs.txt")
        request.log(log)

        with open(logPath, "a") as file:
                for log in request.logs:
                    file.write(log + "\n")
    sys.exit(code)

def has_duplicate(list):
    """Checks if a list has duplicates.

    Args:
        list (_type_): _description_

    Returns:
        _type_: _description_
    """
    seen=set()
    duplicates=[]
    for i in list:
        if i is not None and i in seen:
            duplicates.append(i)
        seen.add(i)
    return duplicates

def convert_seconds(seconds):
    """Given seconds return a string for days, hours and minutes

    Args:
        seconds (_type_): _description_

    Returns:
        _type_: _description_
    """
    days = seconds // (24 * 3600)
    seconds %= (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    return f"{int(days)}Days {int(hours)}Hours {int(minutes)}Minutes"

def get_date_parts(date):
    """Parses a date string to its parts.

    Args:
        date (_type_): _description_

    Returns:
        _type_: _description_
    """
    if date:
        try:
            dateObj=datetime.strptime(date, "%Y-%m-%d")
            day=dateObj.day
            month=dateObj.month
            year=dateObj.year
            return year, month, day
        except ValueError:
            return None, None, None
    else:
        return None, None, None