from math import inf
import cv2
from inference_sdk import InferenceHTTPClient
from deep_sort_realtime.deepsort_tracker import DeepSort
from typing import List, Tuple, Dict
import numpy as np
from scipy.stats import binned_statistic
from itertools import combinations
from processingThreads.videoProcessing.calculate_homography import compute_homography_matrix_cones
from processingThreads.videoProcessing.calculate_speed import compute_speed
from processingThreads.videoProcessing.filter_contours import filter_contours
from os import PathLike
from config import roboflow_key

def extract_from_video(vid:PathLike):

    extracted_frames = []

    capture = cv2.VideoCapture(vid)
    fps = int(capture.get(cv2.CAP_PROP_FPS))

    frame_number = 1
    while capture.isOpened():
        ret, frame = capture.read()

        if not ret:
            break

        extracted_frames.append(frame)

        frame_number += 1

    capture.release()

    return (extracted_frames, fps)


def processVideo(id:str, vid:PathLike)-> tuple[str, Dict[int,float]]:
    """
    Process the provided video input

    Args:
        id (str): SHA256 of the submission, used as ID
        vid (PathLike): Path to the recorded video

    Returns:
        tuple[str, Dict[int,float]]: Processing ID, dict of vehicle ID to speed
    """
    
    CLIENT = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key=roboflow_key
    )

    # Define DeepSort tracker for object tracking across frames
    tracker = DeepSort()

    classes = set(["Scooter-Rider", "bikerider"])
    data = {}
    reference_points = {}
    
    # Define colour of reference point (cones)
    colour = np.uint8([[[232, 0, 4]]]) # orange
    hsv_colour = cv2.cvtColor(colour, cv2.COLOR_RGB2HSV)

    # Define upper and lower bands for the colour range
    lower = np.array((hsv_colour[0][0][0] - 5, 190, 190), dtype=np.uint8)
    upper = np.array((hsv_colour[0][0][0] + 5, 255, 255), dtype=np.uint8)

    # Get video properties, including a list of frames from the video
    extracted_frames, fps = extract_from_video(vid)

    # Detect objects in each frame
    results = CLIENT.infer(extracted_frames, model_id="bikes-ped-scooters/4")

    frame_number = 1
    for result in results:
        frame = extracted_frames[frame_number - 1]
        frame_predictions = result['predictions']

        objects = []

        for p in frame_predictions:
            label = p['class']
            
            # Ignore pedestrians
            if label not in classes:
                continue

            w, h = p["width"], p["height"]
            x, y = p["x"] - w/2, p["y"] - h/2 # (x, y) are top left bounding box co-ords
            confidence = p['confidence']

            objects.append(([x, y, w, h], confidence, label))

        # Track objects

        tracked_objects = tracker.update_tracks(objects, frame=frame)

        for obj in tracked_objects:
            if not obj.is_confirmed():
                continue

            x1, y1, x2, y2 = obj.to_ltrb()
            x, y, w, h = x1, y1, x2 - x1, y2 - y1

            if (x < 0 or y < 0):
                continue

            tracked_id = int(obj.track_id)
            label = obj.det_class

            data.setdefault(tracked_id, [])
            data[tracked_id].append((frame_number, x, y, w, h))        

        # Detect reference points

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # Convert image from original colour space to HSV
        blur_frame = cv2.GaussianBlur(hsv_frame, (5,5), 0) # Blur frame to reduce noise
        mask = cv2.inRange(blur_frame, lower, upper) # Create colour mask

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        filtered_contours = filter_contours(contours, hierarchy)

        # Continue if no reference points found in frame
        if len(filtered_contours) > 0:

            # Get tuple of (x,y) tuples from the filtered contours
            # Increment counter of how many times that reference location has been seen
            reference_index = tuple(cv2.boundingRect(c)[:2] for c in filtered_contours) 
            reference_points.setdefault(reference_index, 0)
            reference_points[reference_index] = reference_points.get(reference_index) + 1 

        frame_number += 1


    # Get most common reference points
    observed_references = list(max(reference_points, key=reference_points.get))

    if len(observed_references) < 2 or len(observed_references) > 5:
        return {}
    elif len(observed_references) > 3:
        # Only take the 3 points that are the most colinear, which will be the 3 points for the cones
        def getArea(p1, p2, p3):
            # Find area of triangle between 3 points
            return 0.5 * abs(p1[0] * (p2[1] * p3[1]) + p2[0](p3[1] - p1[1]) + p3[0](p1[1] - p2[1]))
        
        min_area = inf
        cone_points = []
        for p1, p2, p3 in combinations(observed_references, 3):
            area = getArea(p1, p2, p3)
            if min_area > area:
                cone_points = [p1, p2, p3]
                min_area = area
    else: # len(observed_references) is 2 or 3, this is expected case
        cone_points = observed_references


    # Collate data and pass to another function for calculating the speed of the vehicles
    data = {obj_id: frames for obj_id, frames in data.items() if len(frames) >= fps} # Filter out detected objects that aren't in for at least 1 second

    if len(data) == 0:
        return {}

    homography_matrix = compute_homography_matrix_cones(cone_points)

    return (id, frames_to_speed(data, fps, homography_matrix, cone_points[:2]))


def frames_to_speed(frames: dict[int, List[Tuple[int, float, float, float, float]]], fps: int, homography_matrix, pixel_points):
    speeds = {}
    
    for obj_id, frames in frames.items(): # For each detected object
        frames_array = np.array(frames)
        midpoints = frames_array[:, 1:3] + frames_array[:, 3:5] / 2  # 2D array for x,y coordinates of midpoints
        frame_numbers = frames_array[:, 0]
        weights = 1 / np.diff(frame_numbers) # Calculate weights based on frame differences

        diffs = np.linalg.norm(midpoints[1:] - midpoints[:-1], axis=1) # Calculate shortest differences between consecutive midpoints
        binned_mean = binned_statistic(frame_numbers[1:], diffs * fps * weights, statistic='mean', bins=len(frames) // fps) # Bin data into seconds (groups of fps frames)

        speeds[obj_id] = max(compute_speed(binned_mean.statistic, homography_matrix, reference_points=pixel_points))


    return speeds # Return average speed in pixels per second for each second (group of fps frames) for each detected object
