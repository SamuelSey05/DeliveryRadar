from typing import TypedDict
import os.path

class processingArgs(TypedDict):
    path:os.path
    id:str
    
SIG_END = 0