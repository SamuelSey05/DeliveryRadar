import os.path
from videoQueue.controller import videoQueue
from multiprocessing import Lock, Process
from multiprocessing.connection import Connection
from common import CannotMoveZip, SubmissionError
from videoQueue.commands import OutCommands
from typing import Type

class QueueWrapper():
    _in_con:Connection
    _out_con:Connection
    _p_handle:Process
    _in_l:Type[Lock] # type: ignore
    _out_l:Type[Lock] # type: ignore

    def setup(ctrl):
        _p_handle, _in_con, _out_con = videoQueue(ctrl)
        _in_l = Lock() # Lock for in_con
        _out_l = Lock() # Lock for out_con

setup = QueueWrapper.setup

def upload(loc:os.path) -> str:
    """
    Uploads a new video into the queue

    Args:
        loc (os.path): the location of the .zip file containing the video and `incident.json`
       
    Raises:
        FileNotFoundError: Submission zip not found
        SubmissionError: Submission Failed to Pass Checks
        CannotMoveZip: Cannot move the submission zip to the queue directory
        
    Returns:
        str: sha256 hash of the submission
    """
    QueueWrapper._in_l.acquire()
    QueueWrapper._in_con.send(loc)
    hash, err = QueueWrapper._in_con.recv()
    QueueWrapper._in_l.release()
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

def dequeue(target_dir:os.path) -> str:
    """
    Remove the front submission from the queue into target directory, returning ID of item

    Args:
        dir (os.path): Target directory to copy submission removed
        
    Raises:
        CannotMoveZip: OS was unable to move the zip to the given directory
        FileNotFoundError: Submission is missing from it's stored location, this should never occur unless some kind of cleanup happens on the tempdir during use

    Returns:
        str: sha256 hash of the submission removed, used as ID
    """
    QueueWrapper._out_l.acquire()
    QueueWrapper._out_con.send((OutCommands.DEQUEUE, target_dir))
    hash, err = QueueWrapper._out_con.recv()
    QueueWrapper._out_l.release()
    if err == "":
        return hash
    else:
        # Refuctionalise Errors
        if err == "CannotMoveZip":
            raise CannotMoveZip()
        elif err == "FileNotFound":
            raise FileNotFoundError()

def vq_empty()->bool:
    """
    Test if the Video Queue is empty

    Raises:
        Exception: Any exceptions raised in the VQ Thread are Defunctionalised and Returned, this should never be raised as per initial implementation, but is added for future-proofing

    Returns:
        bool: True=>Empty; False=>Has Items
    """    
    QueueWrapper._out_l.acquire()
    QueueWrapper._out_con.send((OutCommands.EMPTY_QUERY, ""))
    res, err = QueueWrapper._out_con.recv()
    QueueWrapper._out_l.release()
    if err == "":
        return res
    else:
        raise Exception()
