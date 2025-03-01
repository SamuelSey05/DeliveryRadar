from multiprocessing import Process, Queue
from multiprocessing.connection import Connection
from database import insertData
from videoQueue import VideoQueue
from processingThreads import new_thread
from common import processingArgs, TempDir, unzip, zipspec, SIG_END
from common.zipspec import Incident, datetimeFromIncident
from database import DBController
from typing import TypedDict, Tuple, List
from json import load

import os.path, os

class Thread(TypedDict):
    """
    Object for storing associated information managed for each processing thread
    """    
    is_free:bool
    p_handle:Process
    con:Connection
    alive:bool
    procDir:TempDir

class ProcessingController():
    def __init__(self, ctrl:Queue, vq:VideoQueue):
        self.ctrl_con = ctrl
        self.active = True # Used for GC
        self._threads:List[Thread] = []
        self.free_threads = Queue()
        self.db_con = DBController()
        self._ret_q = Queue()
        self.vq = vq
        # TODO Add smarter Thread instantiator - load balancing
        for i in range(4):
            self.add_thread()
        
    def add_thread(self):
        """
        Add a thread to the list of active threads 
        """        
        t:Tuple[Process, Connection] = (new_thread(self._ret_q))
        self._threads.append(Thread(is_free=True, p_handle= t[0], con=t[1], alive=True, procDir=TempDir()))
        self.free_threads.put(len(self._threads)-1)
    
    def processLoop(self):
        """
        Method that runs in the Scheduling Thread
        """        
        while self.active or self.num_running>0:
            if not self.ctrl_con.empty():
                sig = self.ctrl_con.get()
                if sig == SIG_END:
                    self.active = False
                    self.num_running = len(self._threads)-self.free_threads.qsize()

            # If there is a free processing thread, and a video to process
            if not self.free_threads.empty() and not self.vq.vq_empty() and self.active:
                # Get #, and info of thread to use, mark as in use
                t = self.free_threads.pop()
                thr:Thread = self._threads[t]
                thr['is_free'] = False
                # Get submission zip from VQ, unzip and find video file
                submission = self.vq.dequeue(thr['procDir'].path())
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
                if not self.active:
                    self.num_running-=1
        # TODO Cleanup of running Threads
                    
    def __del__(self):
        for thr in self._threads:
            thr['con'].send(SIG_END)
            thr['con'].close()
            thr['p_handle'].join()
            thr['p_handle'].kill()

def controllerThreadFun(con:Connection, vq:VideoQueue):
    """
    Function run in controller Thread

    Args:
        con (Connection): Control Connection for Processing Controller
    """    
    controller = ProcessingController(con, vq)
    controller.processLoop()

def setup_controller(control_con:Connection, vq:VideoQueue)->Process:
    """
    Build a controller Thread, returning process Handle

    Args:
        control_con (Connection): Control Connection for Thread

    Returns:
        Process: handle for process
    """    
    p = Process(target=controllerThreadFun, args=[control_con, vq])
    p.start()
    return p
    
def test_sched():
    from multiprocessing import Pipe
    from time import sleep
    from common import zipspec
    from zipfile import ZipFile
    from os.path import abspath
    from datetime import datetime
    from common import locationClass
    from json import dumps

    vq_ctrl = Queue()
    vq = VideoQueue(vq_ctrl)
    proc_ctrl = Queue()
    proc_p_handle = setup_controller(proc_ctrl, vq)

    for i in range(10):

        with ZipFile("test.zip", "w") as f:
            now = datetime.now()
            incident = zipspec.Incident(location=locationClass(lat = 52.205276, lon = 0.119167), date=zipspec.jsonDate(year=now.year, month=now.month, day=now.day), time=zipspec.jsonTime(hour=now.hour, minute=now.minute, second=now.second), vehicle="Bike")
            f.writestr("incident.json", dumps(incident))
            f.write(abspath("assets/IMG_9927.MOV"), "upload.mov") ## Test with actual video
        vq.upload(abspath("test.zip"))
        sleep(2)

    sleep(20)

    vq_ctrl.put(SIG_END)
    proc_ctrl.put(SIG_END)
    vq.p_handle.join()
    proc_p_handle.join()

    