import os.path
from videoQueue.controller import VideoQueue

_controller = VideoQueue()

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
    _controller.enqueue(loc)

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
    return _controller.dequeue(target_dir)