from tempfile import mkdtemp
from shutil import rmtree
from sys import stderr

class TempDir():
    def __init__(self):
        self._path = mkdtemp()
        
    def __del__(self):
        try:
            rmtree(self._path)
        except OSError:
            print ("Temporary Directory Cannot be Deleted!", file=stderr)
            
    def path(self):
        return self._path
    
    def close(self):
        del self