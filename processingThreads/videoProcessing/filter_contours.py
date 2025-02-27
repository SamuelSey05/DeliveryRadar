import cv2
import numpy as np
from typing import List

# TODO : consider edge cases and error handling

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

    # assume video contains either >1 cone
    # cannot differentiate other objects from reference points
    if len(filtered_contours) < 2:
        return []

    return filtered_contours
