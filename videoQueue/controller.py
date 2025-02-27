from common import hashFile, TempDir, SubmissionError, CannotMoveZip, zipspec, SIG_END
from multiprocessing import Queue, Pipe, Process
from multiprocessing.connection import Connection
from queue import Empty
import os.path
from os import PathLike
from zipfile import is_zipfile, ZipFile
from fnmatch import fnmatch
from json import loads
from videoQueue.commands import OutCommands

class VideoQueue():
    def __init__(self, in_q:Connection=None, out_q:Connection=None, control_con:Connection=None):
        """
        Create a Video Queue

        Args:
            in_q (Connection, optional): Input Connection for multithreading. Defaults to None.
            out_q (Connection, optional): Output Connection for multithreading. Defaults to None.
            control_con (Connection, optional): _description_. Defaults to None.
        """      
        self.active = True  
        self.q = Queue()
        self.in_q = in_q
        self.out_q = out_q
        self.con = Connection
        self.storage = TempDir() ## Create a Temporary Directory for storing the submissions in
        
    def enqueue(self, submission:os.path)->str:
        """
        Enqueues a submission

        Args:
            submission (os.path): path of the submission zip to be processed

        Raises:
            FileNotFoundError: Submission zip not found
            SubmissionError: Submission Failed to Pass Checks
            CannotMoveZip: Cannot move the submission zip to the queue directory
            
        Returns:
            str: sha256 hash of the submission
        """    
        # TODO: Move Zip Verification outside of locked region
        if os.path.exists(submission): ## Check Submission File Exists
            if is_zipfile(submission): ## Check Submission is a ZipFile
                files = []
                with ZipFile(submission, "r") as f:
                    files = f.namelist()
                if len(files) > 2: ## Check Submission Zip contains the correct Files
                    raise SubmissionError(f"Submission contains too many files: {len(files)}/2")
                if len(files) < 2:
                    raise SubmissionError(f"Submission contains too few files: {len(files)}/2")
                if "incident.json" not in files:
                    raise SubmissionError("Cannot find `incident.json`")
                upload = False
                for ext in zipspec.videoExtensions:
                    if f"upload.{ext}" in files:
                        upload = True
                if not upload:
                    raise SubmissionError(f"Cannot find `upload.[{'/'.join(zipspec.videoExtensions)}]`")
                ## Once Submission Checked for Correctness
                fileHash = hashFile(submission)
                try:
                    os.rename(submission, f"{self.storage.path()}/{fileHash}.zip")
                except OSError:
                    raise CannotMoveZip()
                self.q.put(fileHash)

                return fileHash
            else:
                raise SubmissionError("Submission is not a valid ZipFile") 
        else:
            raise FileNotFoundError()
        
    def dequeue(self, dir:os.path)->str:
        """
        Removes a submission from the video queue, moving it to a specified directory, and returning the hash of the submission

        Args:
            dir (os.path): Target directory to move the submission to

        Raises:
            CannotMoveZip: OS was unable to move the zip to the given directory
            FileNotFoundError: Submission is missing from it's stored location, this should never occur unless some kind of cleanup happens on the tempdir during use

        Returns:
            str: sha256 hash of the submission, used as it's ID
        """       
        try: 
            submission = self.q.get(False)
            if os.path.exists(f"{self.storage.path()}/{submission}.zip"):
                try:
                    os.rename(f"{self.storage.path()}/{submission}.zip", f"{dir}/{submission}.zip")
                except OSError:
                    raise CannotMoveZip()
                return submission
            else:
                raise FileNotFoundError()
        except Empty:
            return "EMPTY"
        
    def monitor(self):
        while True:
            if self.con.poll():
                sig = self.con.recv()
                if sig == SIG_END:
                    self.active = False

            if not self.in_q.empty() and self.active:
                submission:PathLike = self.in_q.recv()
                hash = ""
                err = ""
                try:
                    hash = self.enqueue(submission)
                except CannotMoveZip:
                    err = "CannotMoveZip"
                except FileNotFoundError:
                    err = "FileNotFound"
                except SubmissionError as e:
                    err = str(e)
                self.in_q.send((hash, err))

            if not self.out_q.empty() and self.active:
                command:OutCommands
                target:PathLike
                command, target = self.out_q.recv()
                err = ""
                if command == OutCommands.DEQUEUE:
                    hash = ""
                    try:
                        hash = self.dequeue(submission)
                    except CannotMoveZip:
                        err = "CannotMoveZip"
                    except FileNotFoundError:
                        err = "FileNotFound"
                    self.out_q.send((hash, err))
                elif command == OutCommands.EMPTY_QUERY:
                    empty = self.q.empty()
                    self.out_q.send((empty, err))
        # TODO Handle storage of submitted but not yet processed submissions on close
            
        
def test_enqueue(q=VideoQueue()):
    from common import locationClass
    from json import dumps
    with ZipFile("test.zip", "w") as f:
        incident = zipspec.Incident(location=locationClass(lat = 52.205276, lon = 0.119167), date=zipspec.jsonDate(year=1970, month=1, day=1), time=zipspec.jsonTime(hour=0, minute=0, second=0), vehicle="Bike")
        f.writestr("incident.json", dumps(incident))
        f.writestr("upload.mp4", "test") ## TODO: Test with actual video
    q.enqueue(os.path.abspath("test.zip"))
        
def test_dequeue():
    q = VideoQueue()
    test_enqueue(q)
    with TempDir() as temp:
        s = q.dequeue(temp.path())
        print(f"{temp.path()}/{s}.zip")
        input()

if __name__=="__main__":
    VideoQueue.test_enqueue()

def videoQueueThreadFun(in_int:Connection, out_int:Connection, ctrl:Connection):
    """
    Run by the Video Queue Thread

    Args:
        in_int (Connection): Input Connection - for Enqueue commands
        out_int (Connection): Output Connection - for Dequeue and empty commands
        ctrl (Connection): _description_
    """    
    q = VideoQueue(in_int, out_int, ctrl)
    q.monitor()

def videoQueue(ctrl:Connection):
    in_ext, in_int = Pipe()
    out_ext, out_int = Pipe()
    p = Process(target=videoQueueThreadFun, args=[in_int, out_int, ctrl])
    p.start()
    return (p, in_ext, out_ext)
    