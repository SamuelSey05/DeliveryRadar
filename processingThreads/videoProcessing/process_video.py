import os
from common.vehicle_type import VehicleType
import cv2

def processVideo(id:int, vid:os.path, type:VehicleType):
    video = cv2.VideoCapture(vid)
    video.write_videofile(f"processed_videos/processed_{id}.mp4")

    # TODO: Process video

    path = f"processed_videos/processed_{id}.mp4"
    video = cv2.VideoCapture(path)


    os.remove(f"processed_videos/processed_{id}.mp4")
    os.remove(vid)
    pass