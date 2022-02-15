import numpy as np


def get_square_mask(w, h, center_coordinates, radius, color=1):
    mask = np.zeros((w, h), dtype=np.uint8)
    x_start, x_end = center_coordinates[0] - radius, center_coordinates[0] + radius
    y_start, y_end = center_coordinates[1] - radius, center_coordinates[1] + radius

    mask[x_start:x_end, y_start:y_end] = color

    return mask
