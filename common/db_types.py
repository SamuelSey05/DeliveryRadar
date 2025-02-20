from typing import TypedDict
import datetime

class LatLon(TypedDict):
    """
    Type Specification for a Latitude-Longitude Location Object, accessed as a dictionary

    Args:
        lat (float): latitude
        lon (float): longitude
    """    
    lat: float
    lon: float

## ! Deprecated - Use LatLon
class W3W(TypedDict):
    """
    Type Specification for a What3Words based Location Object, accessed as a dictionary

    Args:
        word1 (str) 
        word2 (str)
        word3 (str)
    """    
    word1:str
    word2:str
    word3:str

## Set LatLon as the currently in use Location Object Type
locationClass = LatLon

## Use while testing to mark data entered into the database as Test Data - allows for easy filtering later
test_data = True

class DBRow(TypedDict):
    """
    Type Specification for Data returned from the Database

    Args:
        id (str): sha256 hash of the original zipped submission - used for identification
        speed (float): the speed of a vehicle in the submission
        time (datetime): the date and time of the Incident
        location (locationClass): the Location of the Incident
    """    
    id:str
    speed:float
    time:datetime
    location:locationClass