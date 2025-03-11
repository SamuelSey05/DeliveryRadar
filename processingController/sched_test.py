from os import PathLike
from sys import stderr
from random import random

from typing import Tuple, Dict

def processVideo(id:int, path:PathLike)->Tuple[int, Dict[int, float]]:
    """
    Dummy video processing for testing the scheduler

    Args:
        id (int): ID of the thread performing the processing 
        path (PathLike): Path of the file to process

    Returns:
        Tuple[int, Dict[int, float]]: Processing Thread ID and Dictionary of Vehicle ID -> Speed. Randomly generated single speed for testing
    """    
    print (f"Thread {id}: {path}\n", file=stderr)
    return (id, {0:15*random()})