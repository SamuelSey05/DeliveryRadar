from os import environ

# Enable environment variable to not actually process video and just return dummy data for testing purposes
from processingController.sched_test import processVideo as processVideo_test
from processingThreads.videoProcessing import processVideo as processVideo_prod

if environ.get("DR_TEST_SCHED")!=None:
    processVideo = processVideo_test
else:
    processVideo = processVideo_prod


from multiprocessing import Process, Queue, Manager
from multiprocessing.managers import SyncManager
from threading import Semaphore

from typing import Dict, List, Tuple, Union

from common import processingArgs, SIG_END

import os.path
    
def thread_fun(ctrl_q:Queue, ret_q:Queue, ret_q_shared:Queue, sem:Semaphore):
    """
    Function Performed by Each processing Thread

    Args:
        ctrl_q (Queue): Connection End to Controller
        ret_q (Queue): Connection to Return values down
        ret_q_shared (Queue): Queue to return ID down
    
    Returns(Down Pipe):
        Tuple[str, List[float]]: Will Send (ID, [Speeds]) back along pipe to controller
    """
    data:Union[processingArgs, int] = ctrl_q.get()
    while data != SIG_END:
        vid_id:str = data['vid_id']
        thr_id:int = data['thr_id']
        path:os.path = data['path']
        ret:tuple[str, Dict[int,float]] = processVideo(vid_id, path)
        speeds:List[float] = list(ret[1].values())
        ret_q.put((vid_id, speeds))
        ret_q_shared.put(thr_id)
        sem.release()
        data = ctrl_q.get()

def new_thread(ret_q_shared:Queue, man:SyncManager, sem:Semaphore) -> tuple[Process, Queue, Queue]:   
    """
    Create a new processing Thread and Connection to it

    Args:
        ret_q (Queue): The Queue for data processed to be returned on
        man (SyncManager): Shared Memory Manager for Queues

    Returns:
        tuple[Process, Connection]: Tuple of the processing Thread ID and the Pipe connection to it
    """    
    ctrl_q = man.Queue()
    ret_q = man.Queue()
    p = Process(target=thread_fun, args=[ctrl_q, ret_q, ret_q_shared, sem])
    p.start()
    return (p, ctrl_q, ret_q)
