# from common.vehicle_type import VehicleType
import numpy as np


def compute_speed(
        pixels_per_sec: np.ndarray, 
        homography_matrix: np.ndarray | None, 
        pixels_per_meter: float = 200, 
        reference_points: list[tuple[float, float]] | None = None
        ) -> np.ndarray:
    """
    Convert pixel speed into real-world speed using homography correction.

    Parameters:
    - pixels_per_sec: NumPy array of speeds in pixels per second.
    - homography_matrix: 3x3 matrix for perspective transformation, None if unavailable.
    - pixels_per_meter: Scaling factor (determined from calibration) if homography is not applied.
    - reference_points: List of tuples [(px1, py1), (px2, py2)] in pixel coordinates for mapping homography.

    Returns:
    - speed_kph: NumPy array of speeds in kilometers per hour (km/h).
    """

    def apply_homography_correction(px_per_sec: np.ndarray, homography_matrix: np.ndarray, reference_points: list) -> np.ndarray:
        """
        Adjust pixel speed using homography mapping.

        Parameters:
        - px_per_sec: NumPy array of pixel speeds per second.
        - homography_matrix: 3x3 homography matrix.
        - reference_points: Two points (before and after homography) to estimate real distance.

        Returns:
        - NumPy array of speeds in meters per second.
        """
        if reference_points is None or len(reference_points) != 2:
            return px_per_sec / pixels_per_meter

        # Convert reference points to homogeneous coordinates
        p1 = np.array([reference_points[0][0], reference_points[0][1], 1]).reshape(3, 1)
        p2 = np.array([reference_points[1][0], reference_points[1][1], 1]).reshape(3, 1)

        # Transform points using homography
        real_p1 = np.dot(homography_matrix, p1)
        real_p2 = np.dot(homography_matrix, p2)

        # Normalize homogeneous coordinates
        real_p1 /= real_p1[2]
        real_p2 /= real_p2[2]

        # Compute real-world distance between transformed points
        real_distance = np.linalg.norm(real_p2[:2] - real_p1[:2])

        # Compute scale factor dynamically (pixels per meter)
        pixels_per_meter_dynamic = np.linalg.norm(np.array(reference_points[1]) - np.array(reference_points[0])) / real_distance

        # Convert pixel speed to real-world speed
        return px_per_sec / pixels_per_meter_dynamic

    if homography_matrix is not None:
        real_speed_mps = apply_homography_correction(pixels_per_sec, homography_matrix, reference_points)
    else:
        real_speed_mps = pixels_per_sec / pixels_per_meter

    speed_kph = real_speed_mps * 3.6

    return speed_kph
