from math import inf
import cv2
from ultralytics import YOLO
from typing import List, Tuple, Dict
import numpy as np
from scipy.stats import binned_statistic
from itertools import combinations
from processingThreads.videoProcessing.calculate_homography import compute_homography_matrix_cones
from processingThreads.videoProcessing.calculate_speed import compute_speed
from processingThreads.videoProcessing.filter_contours import filter_contours

def processVideo(id:int, vid:str):
    # TODO : potentially move this somewhere else
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

    if len(observed_references) < 2 or len(observed_references) > 5:
        return {}
    elif len(observed_references) > 3:
        #Only take the 3 points that are the most colinear, which will be the 3 points for the cones
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


    bike_data = {bike_id: frames for bike_id, frames in bike_data.items() if len(frames) >= fps} # Filter out bikes that aren't in for at least 1 second

    if len(bike_data) == 0:
        return {}
    
    frame_id = list(bike_data.values())[0][0][0]

    capture.set(cv2.CAP_PROP_POS_FRAMES, frame_id - 1)
    _, frame = capture.read()


    homography_matrix = compute_homography_matrix_cones(cone_points)

    #print(homography_matrix, pixel_points)

    capture.release()

    return (id, frames_to_speed(bike_data, fps, homography_matrix, cone_points[:2]))


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


print(processVideo(1, "processingThreads/assets/multiple_bikes/mult_bike2.mov"))
