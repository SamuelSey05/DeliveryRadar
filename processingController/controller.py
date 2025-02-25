from multiprocessing import Process
from multiprocessing.connection import Connection 
from queue import Queue
from database import insertData
from videoQueue import dequeue
from processingThreads import new_thread
from common import processingArgs, TempDir, unzip, zipspec, SIG_END
from common.zipspec import Incident, datetimeFromIncident
from database import DBController
from typing import TypedDict, Tuple, List
from time import sleep
from json import load
from datetime import datetime

import os.path, os

class Thread(TypedDict):
    p_handle:Process
    con:Connection
    alive:bool
    procDir:TempDir

class ProcessingController():
    def __init__(self):
        self._threads:List[Thread] = []
        self.free_threads = Queue()
        self.db_con = DBController()
        # TODO Add smarter Thread instantiator - load balancing
        for i in range(4):
            self.free_threads.append(i)
            self.add_thread()
        
    def add_thread(self, num:int):
        t:Tuple[Process, Connection] = (new_thread())
        self._threads.append(Thread(Process = t[0], con=t[1], alive=True, procDir=TempDir()))
    
    def processLoop(self, con:Connection):
        while True:
            if con.poll():
                break # TODO Add safe kill
            if len(self.free_threads) > 0:
                t = self.free_threads.pop()
                thr:Thread = self._threads[t]
                submission = dequeue(thr['procDir'].path())
                unzip(os.path.abspath(f"{thr['procDir'].path()}/{submission}.zip"))
                files = os.listdir(thr['procDir'].path())
                vid = ""
                for ext in zipspec.videoExtensions:
                    if f"upload.{ext}" in files:
                        vid = f"upload.{ext}"
                thr['con'].send(processingArgs(path=f"{thr['procDir'].path()}/{vid}", id=submission))
                
            for i, thr in zip(range(len(self._threads)), self._threads):
                if thr['con'].poll():
                    ret:Tuple[str, List[float]] = thr['con'].recv()
                    # TODO Send to Database
                    with open(f"{thr['procDir'].path()}/incident.json") as jsonObj:
                        incidentData:Incident = load(jsonObj)
                    self.db_con.addIncidents(id=ret[0], speeds=ret[1], time=datetimeFromIncident(incidentData), location=incidentData['location'])
                    thr['procDir'].refresh()
                    self.free_threads.put(i)
                    
    def __del__(self):
        for thr in self._threads:
            thr['con'].send(SIG_END)
            
        sleep(5)
        
        for thr in self._threads:
            thr['p_handle'].kill()
                

def controllerThreadFun(con:Connection):
    controller = ProcessingController()
    controller.processLoop(con)
    
        
        
        
        
    
    