from processingThreads.videoProcessing import processVideo

from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection

from typing import Dict, List, Tuple, Union

from common import processingArgs, SIG_END
    
def thread_fun(con:Connection):
    """
    Function Performed by Each processing Thread

    Args:
        con (Connection): Pipe Connection End to Controller

    Returns(Down Pipe):
        Tuple[str, List[float]]: Will Send (ID, [Speeds]) back along pipe to controller
    """
    data:Union[processingArgs, int] = con.recv()
    while data != SIG_END:
        ret:tuple[str, Dict[int,float]] = processVideo(data['id'], data['path'])
        speeds:List[float] = list(ret[1].values())
        con.send((ret[0], speeds))
        data = con.recv()

def new_thread() -> tuple[Process, Connection]:
    """
    Create a new processing Thread and Connection to it

    Returns:
        tuple[Process, Connection]: Tuple of the processing Thread ID and the Pipe connection to it
    """    
    controller_con, thread_con = Pipe()
    p = Process(target=thread_fun, args=[thread_con])
    p.start()
    return (p, controller_con)
