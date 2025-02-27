from multiprocessing import Process, Queue
from multiprocessing.connection import Connection
from database import insertData
from videoQueue import dequeue, vq_empty
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
    is_free:bool
    p_handle:Process
    con:Connection
    alive:bool
    procDir:TempDir

class ProcessingController():
    def __init__(self):
        self.active = True
        self._threads:List[Thread] = []
        self.free_threads = Queue()
        self.db_con = DBController()
        self._ret_q = Queue()
        # TODO Add smarter Thread instantiator - load balancing
        for i in range(4):
            self.free_threads.append(i)
            self.add_thread()
        
    def add_thread(self, num:int):
        t:Tuple[Process, Connection] = (new_thread(self._ret_q))
        self._threads.append(Thread(is_free=True, Process = t[0], con=t[1], alive=True, procDir=TempDir()))
    
    def processLoop(self, con:Connection):
        while True:
            if con.poll():
                sig = con.recv()
                if sig == SIG_END:
                    self.active = False

            # If there is a free processing thread, and a video to process
            if self.free_threads.empty() and not vq_empty() and self.active:
                # Get #, and info of thread to use, mark as in use
                t = self.free_threads.pop()
                thr:Thread = self._threads[t]
                thr['is_free'] = False
                # Get submission zip from VQ, unzip and find video file
                submission = dequeue(thr['procDir'].path())
                unzip(os.path.abspath(f"{thr['procDir'].path()}/{submission}.zip"))
                files = os.listdir(thr['procDir'].path())
                vid = ""
                for ext in zipspec.videoExtensions:
                    if f"upload.{ext}" in files:
                        vid = f"upload.{ext}"

                # Send path to video file to processing thread
                thr['con'].send(processingArgs(path=f"{thr['procDir'].path()}/{vid}", thr_id=t, vid_id=submission))
            
            if not self._ret_q.empty():
                # Get # of finished Thread
                t:int = self._ret_q.pop()
                thr = self._threads[t]
                # Get Speeds returned by Thread from private channel
                vid_id, speeds = thr['con'].recv()
                
                # Send to Database
                with open(f"{thr['procDir'].path()}/incident.json") as jsonObj:
                    incidentData:Incident = load(jsonObj)
                self.db_con.addIncidents(id=vid_id, speeds=speeds, time=datetimeFromIncident(incidentData), location=incidentData['location'])

                # Clean Thread, refreshing processing tmp and returning to free_threads
                thr['procDir'].refresh()
                thr['is_free']=True
                self.free_threads.put(t)
                    
    def __del__(self):
        for thr in self._threads:
            thr['con'].send(SIG_END)
            
        sleep(5)
        
        for thr in self._threads:
            thr['p_handle'].kill()
                

def controllerThreadFun(con:Connection):
    controller = ProcessingController()
    controller.processLoop(con)

def controller(control_con):
    return Process(target=controllerThreadFun, args=[control_con])
    
        
        
        
        
    
    