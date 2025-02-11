import numpy as np
import cv2

def compute_homography_matrix(pixel_points, real_world_points):
    """
    Computes the homography matrix using pixel and real-world reference points.

    Parameters:
    - pixel_points: List of (x, y) points in pixel coordinates.
    - real_world_points: List of (X, Y) points in real-world meter coordinates.

    Returns:
    - homography_matrix: 3x3 transformation matrix.
    """
    if len(pixel_points) != 4 or len(real_world_points) != 4:
        raise ValueError("Homography requires exactly 4 corresponding points.")

    # Convert to NumPy arrays
    pixel_array = np.array(pixel_points, dtype=np.float32)
    real_world_array = np.array(real_world_points, dtype=np.float32)

    # Compute the homography matrix
    homography_matrix, _ = cv2.findHomography(pixel_array, real_world_array, method=cv2.RANSAC)

    return homography_matrix
