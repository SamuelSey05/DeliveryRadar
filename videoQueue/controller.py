from common import hashFile, TempDir, SubmissionError, CannotMoveZip, zipspec, SIG_END
from multiprocessing import Queue
from threading import Semaphore
from queue import Empty
from os.path import exists, abspath
from os import rename
from os import PathLike
from zipfile import is_zipfile, ZipFile
from videoQueue.commands import OutCommands

class _VideoQueueBase():
    def __init__(self, in_q:Queue=None, out_q:Queue=None, control_con:Queue=None, sem:Semaphore = None):
        """
        Create a Video Queue

        Args:
            in_q (Connection, optional): Input Connection for multithreading. Defaults to None.
            out_q (Connection, optional): Output Connection for multithreading. Defaults to None.
            control_con (Connection, optional): Control Connection. Defaults to None.
        """      
        self.active = True  
        self.q = Queue()
        self.in_q = in_q
        self.out_q = out_q
        self.con = control_con
        self.sem = sem
        self.storage = TempDir() ## Create a Temporary Directory for storing the submissions in
        
    def enqueue(self, submission:PathLike)->str:
        """
        Enqueues a submission

        Args:
            submission (PathLike): path of the submission zip to be processed

        Raises:
            FileNotFoundError: Submission zip not found
            SubmissionError: Submission Failed to Pass Checks
            CannotMoveZip: Cannot move the submission zip to the queue directory
            
        Returns:
            str: sha256 hash of the submission
        """    
        # TODO: Move Zip Verification outside of locked region
        if exists(submission): ## Check Submission File Exists
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
                    rename(submission, f"{self.storage.path()}/{fileHash}.zip")
                except OSError:
                    raise CannotMoveZip()
                self.q.put(fileHash)

                return fileHash
            else:
                raise SubmissionError("Submission is not a valid ZipFile") 
        else:
            raise FileNotFoundError()
        
    def dequeue(self, dir:PathLike)->str:
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
            if exists(f"{self.storage.path()}/{submission}.zip"):
                try:
                    rename(f"{self.storage.path()}/{submission}.zip", f"{dir}/{submission}.zip")
                except OSError:
                    raise CannotMoveZip()
                return submission
            else:
                raise FileNotFoundError()
        except Empty:
            return "EMPTY"
        
    def monitor(self):
        """
        Method to monitor the input Queues and perform necessary enqueues and dequeues without blocking on empty
        """        
        # TODO: Change to Signal/Semaphore Based Responses instead of Polling
        while self.active:
            self.sem.acquire()
            # First check for signal from control connection
            if not self.con.empty():
                sig = self.con.get()
                if sig == SIG_END:
                    print("Deactivating Video Queue Thread")
                    self.active = False

            # Then check for signal from enqueue
            if (not self.in_q.empty()) and self.active:
                command:OutCommands
                target:PathLike
                command, target = self.in_q.get()
                err = None
                # Defunctionalised Commands, Defunctionalise Raised Errors for return
                if command == OutCommands.DEQUEUE:
                    hash = ""
                    try:
                        hash = self.dequeue(target)
                    except CannotMoveZip:
                        err = "CannotMoveZip"
                    except FileNotFoundError:
                        err = "FileNotFound"
                    self.out_q.put((hash, err))
                elif command == OutCommands.EMPTY_QUERY:
                    empty:bool = self.q.empty()
                    self.out_q.put((empty, err))
                elif command == OutCommands.ENQUEUE:
                    hash = ""
                    try:
                        hash = self.enqueue(target)
                    except CannotMoveZip:
                        err = "CannotMoveZip"
                    except FileNotFoundError:
                        err = "FileNotFound"
                    except SubmissionError as e:
                        err = e.msg
                    # Send Result or Defunctionalised Error Back
                    self.out_q.put((hash, err)) 
        # TODO Handle storage of submitted but not yet processed submissions on close
            
        
def test_enqueue(q=_VideoQueueBase()):
    from common import locationClass
    from json import dumps
    with ZipFile("test.zip", "w") as f:
        incident = zipspec.Incident(location=locationClass(lat = 52.205276, lon = 0.119167), date=zipspec.jsonDate(year=1970, month=1, day=1), time=zipspec.jsonTime(hour=0, minute=0, second=0), vehicle="Bike")
        f.writestr("incident.json", dumps(incident))
        f.writestr("upload.mp4", "test") ## TODO: Test with actual video
    q.enqueue(abspath("test.zip"))
        
def test_dequeue():
    q = _VideoQueueBase()
    test_enqueue(q)
    with TempDir() as temp:
        s = q.dequeue(temp.path())
        print(f"{temp.path()}/{s}.zip")
        input()

def videoQueueThreadFun(in_q:Queue, out_q:Queue, ctrl_q:Queue, sem:Semaphore):
    """
    Run by the Video Queue Thread

    Args:
        in_q (Queue): Input Connection - for recieving commands
        out_q (Queue): Output Connection - for returning values/errors
        ctrl_q (Queue): Control Connection
    """    
    q = _VideoQueueBase(in_q, out_q, ctrl_q, sem)
    q.monitor()