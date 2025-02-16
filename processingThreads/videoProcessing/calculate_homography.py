import numpy as np
import cv2


def compute_homography_matrix(frames):
    """
    Automatically extracts reference points from video frames and computes the homography matrix.
    Assumes that the camera perspective is unchanged through the video.

    Parameters:
    - frames: List of video frames.

    Returns:
    - homography_matrix: 3x3 transformation matrix.
    """

    def detect_lane_edges(frame):
        """Detect lane edges using Canny and Hough Transform."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)

        return lines

    def extract_reference_points(lines, frame_shape):
        """Extract bottom-left, bottom-right, top-left, top-right lane reference points."""
        if lines is None:
            return None

        height, width = frame_shape[:2]

        # Store left and right lane points separately
        left_lane = []
        right_lane = []

        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = (y2 - y1) / (x2 - x1 + 1e-6)  # Avoid division by zero

            # Assume negative slope is left lane, positive slope is right lane
            if slope < 0:
                left_lane.append((x1, y1))
                left_lane.append((x2, y2))
            else:
                right_lane.append((x1, y1))
                right_lane.append((x2, y2))

        if not left_lane or not right_lane:
            return None

        # Sort points by y-coordinates (top to bottom)
        left_lane = sorted(left_lane, key=lambda p: p[1])
        right_lane = sorted(right_lane, key=lambda p: p[1])

        # Select bottom-left, bottom-right, top-left, top-right
        pixel_points = [left_lane[-1], right_lane[-1], left_lane[0], right_lane[0]]

        real_world_points = [(0, 0), (2, 0), (0, 10), (2, 10)]  # Assumed lane width 2m, length 10m

        return np.array(pixel_points, dtype=np.float32), np.array(real_world_points, dtype=np.float32)

    # Process the first frame
    first_frame = frames[0]
    lines = detect_lane_edges(first_frame)
    ref_points = extract_reference_points(lines, first_frame.shape)

    if ref_points is None:
        raise ValueError("Failed to extract lane reference points for homography calibration.")

    pixel_points, real_world_points = ref_points

    homography_matrix, _ = cv2.findHomography(pixel_points, real_world_points, method=cv2.RANSAC)

    return homography_matrix
