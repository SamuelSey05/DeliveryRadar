import os
from common.vehicle_type import VehicleType
import cv2
import time
import datetime
import numpy as np

def processVideo(id:int, vid:os.path, type:VehicleType):
    video = cv2.VideoCapture(vid)
    fps = video.get(cv2.CAP_PROP_FPS)
    video.write_videofile(f"processed_videos/processed_{id}.mp4")

    path = f"processed_videos/processed_{id}.mp4"
    video = cv2.VideoCapture(path)

    # TODO: Process video

    os.remove(path)
    os.remove(vid)
    pass