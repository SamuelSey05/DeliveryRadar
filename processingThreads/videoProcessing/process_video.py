import os
# from common.vehicle_type import VehicleType
import cv2
from ultralytics import YOLO
from typing import List, Tuple
import numpy as np
from scipy.stats import binned_statistic

def processVideo(id:int, vid:str):

    # TODO : move this somewhere else, don't what it to run every time the function is called
    model = YOLO('yolo11n.pt')

    # class ID of 'bicycle' in the model
    BIKE_ID = 1

    bike_data = {}
    frame_number = 1

    capture = cv2.VideoCapture(vid)
    
    # Get video properties
    fps = int(capture.get(cv2.CAP_PROP_FPS))

    while capture.isOpened():
        ret, frame = capture.read()

        if not ret:
            break

        results = model.track(source=frame, classes=[BIKE_ID], persist=True)

        boxes = results[0].boxes.xywh.tolist()
        track_ids = results[0].boxes.id.int().tolist() if results[0].boxes.id is not None else []

        for box, bike_id in zip(boxes, track_ids):
            x, y, w, h = box

            if bike_data.get(bike_id) is None:
                bike_data[bike_id] = []
            
            bike_data[bike_id].append((frame_number, x, y, w, h))

        frame_number += 1

    # os.remove(vid)
    
    # print(bike_data)
    # print(fps)

    capture.release()

    return (id, frames_to_speed(bike_data, fps))


def frames_to_speed(frames: List[Tuple[int, float, float, float, float]], fps: int):
    midpoints = np.zeros((len(frames), 2))  # 2D array for x,y coordinates
    weights = np.zeros(len(frames))  # One less weight than frames, to match diffs
    frame_numbers = np.zeros(len(frames))
    prev_j = frames[0][0] - 1
    
    for i, (j, x, y, w, h) in enumerate(frames):
        midpoints[i] = [x + w/2, y + h/2]
        weights[i] = 1/(j - prev_j) # Weight is inversely proportional to the amount of time between frames
        frame_numbers[i] = j
        prev_j = j

    diffs = np.linalg.norm(midpoints[1:] - midpoints[:-1], axis=1) # Calculate shortest differences between consecutive midpoints
    pixels_per_second = diffs * fps * weights[1:] # Convert to pixels per second using weights to account for frames without rectangles

    # Bin data into seconds (groups of fps frames)
    binned_mean = binned_statistic(frame_numbers[1:], pixels_per_second, statistic='mean', bins=len(frames)//fps)

    return binned_mean.statistic # Return average speed in pixels per second for each second (group of fps frames)

# print(processVideo(1, "processingThreads/assets/multiple_bikes/mult_bike1.mov"))