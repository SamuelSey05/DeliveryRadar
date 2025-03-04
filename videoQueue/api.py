from multiprocessing import Lock, Process, Queue, Manager
from multiprocessing.managers import SyncManager
from threading import Semaphore
from typing import Tuple, Type, Optional
from os import PathLike

from videoQueue.controller import videoQueueThreadFun
from videoQueue.commands import OutCommands
from common import CannotMoveZip, SubmissionError

class VideoQueue:
    def __init__(self, ctrl:Queue, man:SyncManager, vq_sem:Semaphore, proc_sem:Semaphore)->Tuple:       
        """
        Create a Multithreaded Video Queue

        Args:
            ctrl (Queue): Control Connection - used for Thread Controls - e.g Kill Signal
            man (Type[Manager]): Global Manager used for creating shared-memory Queues
        """
        command_q = man.Queue()
        ret_q = man.Queue()
        self.sem:Semaphore = vq_sem
        self.proc_sig = proc_sem
        p = Process(target=videoQueueThreadFun, args=[command_q, ret_q, ctrl, vq_sem])
        p.start()
        self.p_handle:Process = p
        self._in:Queue = command_q
        self._out:Queue = ret_q
        self._l:Type[Lock] = Lock() # type: ignore # Lock for commands

    def upload(self, loc:PathLike, debug:bool=False) -> str:
        """
        Uploads a new video into the queue

        Args:
            loc (PathLike): the location of the .zip file containing the video and `incident.json`
        
        Raises:
            FileNotFoundError: Submission zip not found
            SubmissionError: Submission Failed to Pass Checks
            CannotMoveZip: Cannot move the submission zip to the queue directory
            
        Returns:
            str: sha256 hash of the submission
        """
        if debug:
            print("Acquire lock")
        self._l.acquire()
        if debug:
            print("Lock Acquired")
        self._in.put((OutCommands.ENQUEUE, loc))
        self.sem.release()
        if debug:
            print("Enqueue Requested")
        hash:str
        err:Optional[str]
        hash, err = self._out.get()
        if debug:
            print("Enqueue Results recieved, releasing lock")
        self._l.release()
        if debug:
            print(f"Lock Released\nResponse: {hash} / {err}")
        if err == None:
            self.proc_sig.release()
            return hash
        else:
            # Refunctionalise Errors
            if err == "CannotMoveZip":
                raise CannotMoveZip()
            elif err == "FileNotFound":
                raise FileNotFoundError()
            else:
                raise SubmissionError(err)

    def dequeue(self, target_dir:PathLike) -> str:
        """
        Remove the front submission from the queue into target directory, returning ID of item

        Args:
            dir (PathLike): Target directory to copy submission removed
            
        Raises:
            CannotMoveZip: OS was unable to move the zip to the given directory
            FileNotFoundError: Submission is missing from it's stored location, this should never occur unless some kind of cleanup happens on the tempdir during use

        Returns:
            str: sha256 hash of the submission removed, used as ID
        """
        self._l.acquire()
        self._in.put((OutCommands.DEQUEUE, target_dir))
        self.sem.release()
        hash, err = self._out.get()
        self._l.release()
        if err == None:
            return hash
        else:
            # Refuctionalise Errors
            if err == "CannotMoveZip":
                raise CannotMoveZip()
            elif err == "FileNotFound":
                raise FileNotFoundError()

    def vq_empty(self)->bool:
        """
        Test if the Video Queue is empty

        Raises:
            Exception: Any exceptions raised in the VQ Thread are Defunctionalised and Returned, this should never be raised as per initial implementation, but is added for future-proofing

        Returns:
            bool: True=>Empty; False=>Has Items
        """    
        self._l.acquire()
        self._in.put((OutCommands.EMPTY_QUERY, ""))
        self.sem.release()
        res, err = self._out.get()
        self._l.release()
        if err == None:
            return res
        else:
            raise Exception()
    
