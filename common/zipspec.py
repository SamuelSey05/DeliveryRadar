from typing import TypedDict
from datetime import datetime

from common.db_types import locationClass

videoExtensions = ("mp4", "mov", "mkv", "MOV")

class jsonDate(TypedDict):
    year:int
    month:int
    day:int
    
class jsonTime(TypedDict):
    hour:int
    minute:int
    second:int

class Incident(TypedDict):
    location:locationClass
    date:jsonDate
    time:jsonTime
    vehicle:str
    
def datetimeFromIncident(inc:Incident)->datetime:
    return datetime(inc["date"]["year"], inc["date"]["month"], inc["date"]["day"], inc["time"]["hour"], inc["time"]["minute"], inc["time"]["second"])