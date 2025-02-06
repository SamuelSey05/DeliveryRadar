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
    midpoints = np.zeros((len(frames), 2))  # 2D array for x,y coordinates
    weights = np.zeros(len(frames))  # One less weight than frames, to match diffs
    prev_j = frames[0][0] - 1
    
    for i, (j, x, y, w, h) in enumerate(frames):
        midpoints[i] = [x + w/2, y + h/2]
        weights[i] = 1/(j - prev_j) # Weight is inversely proportional to the amount of time between frames
        prev_j = j

    diffs = np.linalg.norm(midpoints[1:] - midpoints[:-1], axis=1) # Calculate shortest differences between consecutive midpoints
    pixels_per_second = diffs * fps * weights[1:] # Convert to pixels per second using weights to account for frames without rectangles

    return np.average(pixels_per_second) # Return average speed in pixels per second
