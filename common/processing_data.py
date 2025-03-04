from typing import TypedDict
from os import PathLike

class processingArgs(TypedDict):
    path:PathLike
    vid_id:str
    thr_id:int
    
SIG_END = 0
