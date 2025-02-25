import os.path
import cv2
import cv2

from common import VehicleType
from .process_video import processVideo  

def processVideo(id: int, vid: os.path, vehicle_type:VehicleType):


    # TODO convert vid to mp4 ???


    # get video capture
    capture = cv2.VideoCapture(vid)

    pass