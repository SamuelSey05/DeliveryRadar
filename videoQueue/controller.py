from queue import Queue
import os.path
from common import hashFile, TempDir, SubmissionError, CannotMoveZip, zipspec
from zipfile import is_zipfile, ZipFile
from fnmatch import fnmatch
from json import loads

class VideoQueue():
    def __init__(self):
        self.q = Queue()
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
                    raise SubmissionError(f"Cannot find `upload.[{"/".join(zipspec.videoExtensions)}]`")
                ## Once Submission Checked for Correctness
                fileHash = hashFile(submission)
                try:
                    os.rename(submission, f"{self.storage.path()}/{fileHash}.zip")
                except OSError:
                    raise CannotMoveZip
                self.q.put(fileHash)

                return fileHash
            else:
                raise SubmissionError("Submission is not a valid ZipFile") 
        else:
            raise FileNotFoundError()