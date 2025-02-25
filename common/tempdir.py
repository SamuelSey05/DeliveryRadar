from tempfile import mkdtemp
from shutil import rmtree
from sys import stderr

class TempDir():
    def __init__(self):
        self._open()
        
    def __del__(self):
        self._close()
    
    def _open(self):
        self._path = mkdtemp()
    
    def _close(self):   
        try:
            rmtree(self._path)
        except OSError:
            print ("Temporary Directory Cannot be Deleted!", file=stderr)   
      
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        del self
            
    def path(self):
        return self._path
    
    def close(self):
        del self
        
    def refresh(self):
        self._close()
        self._open()