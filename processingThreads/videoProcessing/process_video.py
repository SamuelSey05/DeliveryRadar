import os
from common.vehicle_type import VehicleType
import cv2
import time
import datetime
import numpy as np
from typing import List, Tuple

def processVideo(id:int, vid:os.path, type:VehicleType):
    video = cv2.VideoCapture(vid)
    fps = video.get(cv2.CAP_PROP_FPS)
    video.write_videofile(f"processed_videos/processed_{id}.mp4") # Make video file format uniform in MP4

    path = f"processed_videos/processed_{id}.mp4"
    video = cv2.VideoCapture(path)

    # TODO: Process video

    os.remove(path)
    os.remove(vid) # Clean up
    pass

def frames_to_speed(frames: List[Tuple[float, float, float, float]], fps: int):
    midpoints = np.zeros(len(frames))
    for i, (x, y, w, h) in enumerate(frames):
        midpoints[i] = (x + w/2, y + h/2) # Get midpoint of rectangle in frame

    diffs = midpoints[1:] - midpoints[:-1] # Calculate differences between consecutive midpoints
    pixels_per_second = diffs * fps # Convert to pixels per second

    return pixels_per_second / len(frames) # Return average speed in pixels per second