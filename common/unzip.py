from zipfile import ZipFile
import os.path

def unzip(path:os.path):
    dir = os.path.dirname(path)
    with ZipFile(path, "r") as zip:
        zip.extractall(dir)
    return True