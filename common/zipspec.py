from typing import TypedDict

from common.db_types import locationClass

videoExtensions = ("mp4", "mov", "mkv")

class jsonDate(TypedDict):
    "year":int
    "month":int
    "day":int
    
class jsonTime(TypedDict):
    "hour":int
    "minute":int
    "second":int

class Incident(TypedDict):
    location:locationClass
    date:jsonDate
    time:jsonTime
    vehicle:str