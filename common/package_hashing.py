import hashlib
import os.path

def hashFile(path: os.path) -> str:
    """
    Returns an SHA256 Hash of a given file, including a zip file

    Args:
        path (os.path): Absolute Path to the file, probably using `os.path.abspath("filename.ext")`

    Returns:
        str: SHA256 hash of the file
    """    
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()