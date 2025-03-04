import os.path
import cv2
import cv2

from common import VehicleType
from processingThreads.videoProcessing.process_video import processVideo  


def processVideo(id: int, vid: os.path, vehicle_type:VehicleType):

    # get video capture
    capture = cv2.VideoCapture(vid)
