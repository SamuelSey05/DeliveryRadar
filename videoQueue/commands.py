from enum import Enum

class OutCommands(Enum):
    """
    Enumeration of possible commands sent along output pipe
    """    
    DEQUEUE = 0
    EMPTY_QUERY = 1
