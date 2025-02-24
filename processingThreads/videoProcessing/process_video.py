import os
import time
# from common.vehicle_type import VehicleType
import cv2
from ultralytics import YOLO
from typing import List, Tuple, Dict
import numpy as np
from scipy.stats import binned_statistic
from processingThreads.videoProcessing.calculate_homography import compute_homography_matrix
from processingThreads.videoProcessing.calculate_speed import compute_speed

def filter_contours(contours: List[np.ndarray], hierarchy: List[np.ndarray]):
    pass

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

        for box, id in zip(boxes, track_ids):
            x, y, w, h = box

            if bike_data.get(id) is None:
                bike_data[id] = []
            
            bike_data[id].append((frame_number, x, y, w, h))

        frame_number += 1

    # os.remove(vid)


    bike_data = {bike_id: frames for bike_id, frames in bike_data.items() if len(frames) >= fps} # Filter out bikes that aren't in for at least 1 second

    if len(bike_data) == 0:
        return {}
    
    frame_id = list(bike_data.values())[0][0][0]

    capture.set(cv2.CAP_PROP_POS_FRAMES, frame_id - 1)
    _, frame = capture.read()

    homography_matrix, pixel_points = compute_homography_matrix(frame)

    #print(homography_matrix, pixel_points)

    capture.release()

    return (id, frames_to_speed(bike_data, fps, homography_matrix, pixel_points))


def frames_to_speed(bikes_frames: dict[int, List[Tuple[int, float, float, float, float]]], fps: int, homography_matrix, pixel_points):
    speeds = {}
    
    for bike_id, frames in bikes_frames.items(): # For each bike
        frames_array = np.array(frames)
        midpoints = frames_array[:, 1:3] + frames_array[:, 3:5] / 2  # 2D array for x,y coordinates of midpoints
        frame_numbers = frames_array[:, 0]
        weights = 1 / np.diff(frame_numbers) # Calculate weights based on frame differences

        diffs = np.linalg.norm(midpoints[1:] - midpoints[:-1], axis=1) # Calculate shortest differences between consecutive midpoints
        binned_mean = binned_statistic(frame_numbers[1:], diffs * fps * weights, statistic='mean', bins=len(frames) // fps) # Bin data into seconds (groups of fps frames)
        # speeds[bike_id] = binned_mean.statistic

        speeds[bike_id] = max(compute_speed(binned_mean.statistic, homography_matrix, reference_points=pixel_points))

    return speeds # Return average speed in pixels per second for each second (group of fps frames) for each bike


#print(processVideo(1, "processingThreads/assets/multiple_bikes/mult_bike2.mov"))