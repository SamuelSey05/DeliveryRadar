import os
# from common.vehicle_type import VehicleType
import cv2
from ultralytics import YOLO
from typing import List, Tuple, Dict
import numpy as np
from scipy.stats import binned_statistic

def processVideo(id: int, vid: str):
    model = YOLO('yolo11n.pt')
    BIKE_ID = 1
    bike_data: Dict[int, List[Tuple[int, float, float, float, float]]] = {}
    frame_number = 0

    capture = cv2.VideoCapture(vid)
    fps = int(capture.get(cv2.CAP_PROP_FPS))

    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            break

        results = model.track(source=frame, classes=[BIKE_ID], persist=True)
        boxes = results[0].boxes.xywh.tolist()
        track_ids = results[0].boxes.id.int().tolist() if results[0].boxes.id is not None else []

        for box, track_id in zip(boxes, track_ids):
            x, y, w, h = box
            if track_id not in bike_data:
                bike_data[track_id] = []
            bike_data[track_id].append((frame_number, x, y, w, h))

        frame_number += 1

    capture.release()
    return frames_to_speed(bike_data, fps)

def frames_to_speed(bikes_frames: Dict[int, List[Tuple[int, float, float, float, float]]], fps: int) -> Dict[int, np.ndarray]:
    speeds = {}

    for bike_id, frames in bikes_frames.items(): # For each bike
        if len(frames) < 2:
            continue
        frames_array = np.array(frames)
        midpoints = frames_array[:, 1:3] + frames_array[:, 3:5] / 2  # 2D array for x,y coordinates
        frame_numbers = frames_array[:, 0]
        weights = 1 / np.diff(frame_numbers) # Calculate weights based on frame differences

        diffs = np.linalg.norm(midpoints[1:] - midpoints[:-1], axis=1) # Calculate shortest differences between consecutive midpoints

        # Bin data into seconds (groups of fps frames)
        binned_mean = binned_statistic(frame_numbers[1:], diffs * fps * weights, statistic='mean', bins=len(frames) // fps)
        speeds[bike_id] = binned_mean.statistic

    return speeds # Return average speed in pixels per second for each second (group of fps frames) for each bike

print(processVideo(1, "processingThreads/assets/multiple_bikes/mult_bike1.mov"))