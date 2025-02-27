from processingThreads.videoProcessing import processVideo

from multiprocessing import Pipe, Process, Queue
from multiprocessing.connection import Connection

from typing import Dict, List, Tuple, Union

from common import processingArgs, SIG_END

import os.path
    
def thread_fun(con:Connection, ret_q:Queue):
    """
    Function Performed by Each processing Thread

    Args:
        con (Connection): Pipe Connection End to Controller

    Returns(Down Pipe):
        Tuple[str, List[float]]: Will Send (ID, [Speeds]) back along pipe to controller
    """
    data:Union[processingArgs, int] = con.recv()
    while data != SIG_END:
        vid_id:str = data['vid_id']
        thr_id:int = data['thr_id']
        path:os.path = data['path']
        ret:tuple[str, Dict[int,float]] = processVideo(vid_id, path)
        speeds:List[float] = list(ret[1].values())
        con.send((vid_id, speeds))
        ret_q.put(thr_id)
        data = con.recv()

def new_thread(ret_q:Queue) -> tuple[Process, Connection]:   
    """
    Create a new processing Thread and Connection to it

    Args:
        ret_q (Queue): The Queue for data processed to be returned on

    Returns:
        tuple[Process, Connection]: Tuple of the processing Thread ID and the Pipe connection to it
    """    
    controller_con, thread_con = Pipe()
    p = Process(target=thread_fun, args=[thread_con, ret_q])
    p.start()
    return (p, controller_con)
