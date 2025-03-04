from database.controller import DBController
from common.db_types import locationClass, DBRow
from typing import List
import datetime

_controller = DBController()

def insertData(id:str, speeds:List[float], time:datetime, location:locationClass):
    """
    Insert an incident submission to the database

    Args:
        id (str): sha256 hash of the submission, used for identification
        speeds (List[float]): List of the speeds of the vehicles identified in the Incident
        time (datetime): Time of the Incident
        location (locationClass): Location of the Incident
    """    
    _controller.addIncidents(id, speeds, time, location)

# TODO this is not serialising
def getIncidents()->List[DBRow]:
    """
    Returns the Incidents stored in the database for processing into the heatmap

    Returns:
        List[DBRow]: List of the Incidents recorded, some IDs may appear twice where multiple vehicles were observed in the incident
    """      
    return _controller.getIncidents()
    
