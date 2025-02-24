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
    # filter out any bounding boxes that have parents (i.e. boxes that are completely within another box)
    parent_contours = [contours[i] for i in range(len(contours)) if hierarchy[0][i][3] == -1]

    dimensions = {}

    # populate dimensions
    for i, c in enumerate(parent_contours):
        x, y, w, h = cv2.boundingRect(c)
        dimensions[i] = {
            "bounding_box": (x, y, w, h),
            "area": w * h,
            "centre": (x + w/2, y + h/2)
        }

    filtered_contours = []
    
    # check if bounding box i has a smaller area than bounding box j, and i has a centre point near j ...
    # ... if so, do not add bounding box to filtered_contours as it is likely noise related to the box with the larger area
    for i, i_contour in enumerate(parent_contours):
        removable = False

        i_A = dimensions[i]["area"]
        i_cx, i_cy = dimensions[i]["centre"]

        for j in range(len(parent_contours)):
            # do not compare box to itself
            if (i == j):
                continue

            j_x, j_y, j_w, j_h = dimensions[j]["bounding_box"]
            j_A = dimensions[j]["area"]
            
            # make size and locality comparisons
            if (j_x - j_w <= i_cx <= j_x + 2*j_w) and (j_y -j_h <= i_cy <= j_y + 2*j_h) and (i_A < j_A):
                removable = True
                break
        
        # append to filtered_contours if suitable reference point
        if not removable:
            filtered_contours.append(i_contour)

    # assume video contains either 2 or 3 cones
    # cannot differentiate other objects from reference points
    if not (len(filtered_contours) == 2 or len(filtered_contours) == 3):
        return []

    return filtered_contours

def processVideo(id:int, vid:str):

    # TODO : move this somewhere else, don't what it to run every time the function is called
    model = YOLO('yolo11n.pt')

    # class ID of 'bicycle' in the model
    BIKE_ID = 1

    bike_data = {}
    
    # define colour of reference point (cones)
    colour = np.uint8([[[232, 0, 4]]]) # orange
    hsv_colour = cv2.cvtColor(colour, cv2.COLOR_RGB2HSV)

    # define upper and lower bands for the colour range
    lower = np.array((hsv_colour[0][0][0] - 5, 190, 190), dtype=np.uint8)
    upper = np.array((hsv_colour[0][0][0] + 5, 255, 255), dtype=np.uint8)

    reference_points = {}

    # get video properties
    capture = cv2.VideoCapture(vid)
    fps = int(capture.get(cv2.CAP_PROP_FPS))

    frame_number = 1

    while capture.isOpened():
        ret, frame = capture.read()

        if not ret:
            break

        # detect bikes

        results = model.track(source=frame, classes=[BIKE_ID], persist=True)

        boxes = results[0].boxes.xywh.tolist()
        track_ids = results[0].boxes.id.int().tolist() if results[0].boxes.id is not None else []

        for box, id in zip(boxes, track_ids):
            x, y, w, h = box

            if bike_data.get(id) is None:
                bike_data[id] = []
            
            bike_data[id].append((frame_number, x, y, w, h))

        frame_number += 1

        # detect reference points

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # convert image from original colour space to HSV
        blur_frame = cv2.GaussianBlur(hsv_frame, (5,5), 0) # blur frame to reduce noise
        mask = cv2.inRange(blur_frame, lower, upper) # create colour mask

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        filtered_contours = filter_contours(contours, hierarchy)

        # continue if no reference points found in frame
        if len(filtered_contours) == 0:
            continue 

        # get tuple of (x,y) tuples from the filtered contours
        # increment counter of how many times that reference location has been seen
        reference_index = tuple(cv2.boundingRect(c)[:2] for c in filtered_contours) 
        reference_points[reference_index] = reference_points.get(reference_index, 0) + 1 

    # os.remove(vid)

    # get most common reference points
    # TODO : pass this to another function for distance calculation
    observed_references = list(max(reference_points, key=reference_points.get))

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