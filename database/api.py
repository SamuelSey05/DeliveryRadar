## TODO

from controller import DBController

_controller = DBController()

def insertData():
    pass

def getIncidents():
    """
    Returns a list of (location (3-Tuple of String), vehicle type (Enum), time (DateTime), speed (Float)) tuples
    """     
    return _controller.getIncidents()
    
