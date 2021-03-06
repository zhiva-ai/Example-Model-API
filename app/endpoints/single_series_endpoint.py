import orjson
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from app.docker_logs import get_logger
from typing import List, Dict, Any
import io
import pydicom
import json
import numpy as np
from app.endpoints.utils import mock_up_inference

router = APIRouter(prefix="/single-series-endpoint")

logger = get_logger("single-series-endpoint-logger")


@router.post("/predict", response_class=ORJSONResponse)
async def predict(items: List[str]):
    """
    :param items:
    :return: json in the specified format
    """
    instances = [
        pydicom.dcmread(io.BytesIO(bytes(json.loads(instance)))) for instance in items
    ]

    instances.sort(key=lambda i: i.InstanceNumber)
    logger.info(f"{len(instances)} instances in series")
    study_uid = str(instances[0].StudyInstanceUID)
    series_uid = str(instances[0].SeriesInstanceUID)

    instances_uids = [str(i.SOPInstanceUID) for i in instances]

    masks = mock_up_inference(instances)

    series_metadata = [
        {
            "dataType": "text",
            "value": f"{len(instances)} instances in series",
            "title": "Series metadata",
            "description": "Here you may put the description of the metadata for a study",
        }
    ]

    instances_metadata = [
        [{"dataType": "text", "value": f"Instance: {i+1}", "title": "Series metadata"}]
        for i in range(len(instances))
    ]

    return generate_json_response(
        study_uid,
        series_uid,
        instances_uids,
        masks,
        series_metadata,
        instances_metadata,
    )


def generate_json_response(
    study_uid: str,
    series_uid: str,
    instances_uids: List[str],
    masks: np.ndarray,
    series_metadata: List[Dict[str, Any]],
    instances_metadata: List[List[Dict[str, Any]]],
    mask_name="Example",
    mask_description="Example mask description",
    color="lightskyblue",
    class_color="lightskyblue",
    active_color="aquamarine",
) -> bytes:

    instances_dict = {}

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
        instances_dict[i_uid] = {"segments": segments, "metadata": i_metadata}

    instances_dict["metadata"] = series_metadata

    study_dict = {
        study_uid: {
            series_uid: instances_dict,
        }
    }
    return orjson.dumps(study_dict)
