class SubmissionError(Exception):
    def __init__(self, message="Submission Failed to parse"):
        super().__init__(message)
        self.msg = message

class CannotMoveZip(Exception):
    pass