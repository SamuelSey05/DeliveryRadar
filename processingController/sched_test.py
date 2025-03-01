from os import PathLike
from sys import stderr
from random import random

def processVideo(id:int, path:PathLike):
    print (f"Thread {id}: {path}\n", file=stderr)
    return (id, {0:15*random()})