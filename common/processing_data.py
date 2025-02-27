from typing import TypedDict
import os.path

class processingArgs(TypedDict):
    path:os.path
    vid_id:str
    thr_id:int
    
SIG_END = 0