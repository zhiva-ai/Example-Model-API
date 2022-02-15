import orjson
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from app.docker_logs import get_logger
from typing import List, Dict, Any
import io
import pydicom
from pydicom.dataset import FileDataset
import json
import numpy as np
from app.endpoints.utils import get_square_mask

router = APIRouter(prefix="/single-series-endpoint")

logger = get_logger("single-series-endpoint-logger")


@router.post("/predict", response_class=ORJSONResponse)
async def predict(items: List[str]):
    """
    :param items:
    :return: json in the specified format
    """
    instances = [
        pydicom.dcmread(io.BytesIO(bytes(json.loads(instance))))
        for instance in items
    ]

    instances.sort(key=lambda i: i.InstanceNumber)
    logger.info(f"{len(instances)} instances in series")
    study_instance_uid = str(instances[0].StudyInstanceUID)
    series_instance_uid = str(instances[0].SeriesInstanceUID)

    instances_uids = [str(i.SOPInstanceUID) for i in instances]
    # mapping = {str(i.InstanceNumber): str(i.SOPInstanceUID) for i in instances}

    masks = inference(instances)

    series_metadata = [{
        "dataType": "text",
        "value": f"{len(instances)} instances in series",
        "title": "Series metadata",
        "description": "Here you may put the description of the metadata for a study",
    }]

    instances_metadata = [[{"dataType": "text", "value": f"Instance: {i+1}", "title": "Series metadata"}] for i in range(len(instances))]

    return convert_lungs_prediction_to_json_response(
        study_instance_uid,
        series_instance_uid,
        instances_uids,
        masks,
        series_metadata,
        instances_metadata
    )


def inference(instances: List[FileDataset]) -> np.ndarray:
    """
    A function that acts as a model inference mock-up. For each frame we assign a square mask
    :param instances:
    :return: mask of squares for each frame of shape (frames, w, h)
    """
    w, h = instances[0].pixel_array.shape
    radius = w // 5
    center_coordinates = (w // 2, h // 2)

    return np.stack([get_square_mask(w, h, center_coordinates, radius) for _ in instances], axis=0)


def convert_lungs_prediction_to_json_response(
        study_instance_uid: str,
        series_instance_uid: str,
        instances_uids: List[str],
        masks: np.ndarray,
        series_metadata: List[Dict[str, Any]],
        instances_metadata: List[List[Dict[str, Any]]],
        # instances_metadata,
        mask_name="Example",
        mask_description="Example mask description",
        color="lightskyblue",
        class_color="lightskyblue",
        active_color="aquamarine",
) -> bytes:

    instances = {}

    for idx, (i_uid, i_metadata) in enumerate(zip(instances_uids, instances_metadata)):
        single_mask = {
            "points": masks[idx].tolist(),
            "color": color,
            "classColor": class_color,
            "activeColor": active_color,
            "className": mask_name,
            "description": mask_description,
        }
        segments = [single_mask]
        instances[i_uid] = {"segments": segments, "metadata": i_metadata}

    instances["metadata"] = series_metadata

    final_dict = {
        study_instance_uid: {
            series_instance_uid: instances,
        }
    }
    return orjson.dumps(final_dict)
