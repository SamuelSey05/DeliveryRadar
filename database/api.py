from database.controller import DBController
from common.db_types import locationClass
from typing import List
import datetime

_controller = DBController()

def insertData(id:str, speeds:List[float], time:datetime, location:locationClass):
    _controller.addIncidents(id, speeds, time, location)

def getIncidents():
    """
    Returns a list of (location (3-Tuple of String), vehicle type (Enum), time (DateTime), speed (Float)) tuples
    """     
    return _controller.getIncidents()
    
