from multiprocessing import Pipe, Lock, Process
from multiprocessing.connection import Connection
from typing import Tuple
from os import PathLike

from videoQueue.controller import videoQueueThreadFun
from videoQueue.commands import OutCommands
from common import CannotMoveZip, SubmissionError

class VideoQueue:
    def __init__(self, ctrl:Connection)->Tuple:
        """
        Create a Multithreaded Video Queue

        Args:
            ctrl (Connection): Control Connection - used for Thread Controls - e.g Kill Signal
        """    
        in_ext, in_int = Pipe()
        out_ext, out_int = Pipe()
        p = Process(target=videoQueueThreadFun, args=[in_int, out_int, ctrl])
        p.start()
        self.p_handle:Process = p
        self._in:Connection = in_ext
        self._out:Connection = out_ext
        self._in_l:Type[Lock] = Lock() # type: ignore # Lock for in_con
        self._out_l:Type[Lock] = Lock() # type: ignore # Lock for out_con

    def upload(self, loc:PathLike) -> str:
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
        self._in_l.acquire()
        self._in.send(loc)
        hash, err = self._in.recv()
        self._in_l.release()
        if err == "":
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
        self._out_l.acquire()
        self._out.send((OutCommands.DEQUEUE, target_dir))
        hash, err = self._out.recv()
        self._out_l.release()
        if err == "":
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
        self._out_l.acquire()
        self._out.send((OutCommands.EMPTY_QUERY, ""))
        res, err = self._out.recv()
        self._out_l.release()
        if err == "":
            return res
        else:
            raise Exception()
    
