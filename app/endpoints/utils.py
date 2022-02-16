import numpy as np
from typing import List
from pydicom import FileDataset


def get_square_mask(w, h, center_coordinates, radius, color=1):
    mask = np.zeros((w, h), dtype=np.uint8)
    x_start, x_end = center_coordinates[0] - radius, center_coordinates[0] + radius
    y_start, y_end = center_coordinates[1] - radius, center_coordinates[1] + radius

    mask[x_start:x_end, y_start:y_end] = color

    return mask


def mock_up_inference(
    instances: List[FileDataset], radius_factor: float = 0.2
) -> np.ndarray:
    """
    A function that acts as a model inference mock-up. For each frame we assign a square mask
    :param radius_factor:
    :param instances:
    :return: mask of squares for each frame of shape (frames, w, h)
    """
    w, h = instances[0].pixel_array.shape
    radius = int((w+h) / 2 * radius_factor)
    center_coordinates = (w // 2, h // 2)

    return np.stack(
        [get_square_mask(w, h, center_coordinates, radius) for _ in instances], axis=0
    )
