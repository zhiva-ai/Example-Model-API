import numpy as np
from typing import List
from pydicom import FileDataset


def get_square_mask(w, h, center_coordinates, radius, color=1):
    mask = np.zeros((w, h), dtype=np.uint8)
    x_start, x_end = center_coordinates[0] - radius, center_coordinates[0] + radius
    y_start, y_end = center_coordinates[1] - radius, center_coordinates[1] + radius

    mask[x_start:x_end, y_start:y_end] = color

    return mask


def get_square_annotation_list(w, h, center_coordinates, radius):
    color = 1

    mask = np.zeros((w, h), dtype=np.uint8)
    x_start, x_end = center_coordinates[0] - radius, center_coordinates[0] + radius
    y_start, y_end = center_coordinates[1] - radius, center_coordinates[1] + radius

    # print("x_start:", x_start, "x_end:", x_end, "y_start:", y_start, "y_end:", y_end)

    mask[x_start : (x_end + 1), y_start] = color
    mask[x_start : (x_end + 1), y_end] = color

    mask[x_start, y_start : (y_end + 1)] = color
    mask[x_end, y_start : (y_end + 1)] = color

    return [[x_start, y_start], [x_end, y_start], [x_end, y_start], [x_end, y_end], [x_start, y_start]]

    # return np.argwhere(mask == color).tolist()


def mock_up_inference_annotation(
    instances: List[FileDataset], radius_factor: float = 0.2
):
    """
    A function that acts as a model inference mock-up. For each frame we assign a square mask
    :param radius_factor:
    :param instances:
    :return:
    """
    w, h = instances[0].pixel_array.shape
    radius = int((w + h) / 2 * radius_factor)
    center_coordinates = (w // 2, h // 2)

    return [
        get_square_annotation_list(w, h, center_coordinates, radius) for _ in instances
    ]


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
    radius = int((w + h) / 2 * radius_factor)
    center_coordinates = (w // 2, h // 2)

    return np.stack(
        [get_square_mask(w, h, center_coordinates, radius) for _ in instances], axis=0
    )
