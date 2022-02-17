import orjson
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from app.docker_logs import get_logger
from typing import List, Dict, Any
import io
import pydicom
import numpy as np
import json

from app.endpoints.utils import mock_up_inference, mock_up_inference_annotation

SERIES_ONE_KEY = "series-one"
SERIES_TWO_KEY = "series-two"

router = APIRouter(prefix="/multiple-series-annotation-endpoint")

logger = get_logger("multiple-series-endpoint-annotation-logger")


@router.post("/predict", response_class=ORJSONResponse)
async def predict(items: Dict[str, Dict[str, List[str]]]):
    """
    :param items:
    :return: json in the specified format
    """

    series_one_instances = [
        pydicom.dcmread(io.BytesIO(bytes(json.loads(instance))))
        for instance in items[SERIES_ONE_KEY]["data"]
    ]
    series_one_instances.sort(key=lambda i: i.InstanceNumber)

    series_two_instances = [
        pydicom.dcmread(io.BytesIO(bytes(json.loads(instance))))
        for instance in items[SERIES_TWO_KEY]["data"]
    ]
    series_two_instances.sort(key=lambda i: i.InstanceNumber)

    study_uid = str(series_one_instances[0].StudyInstanceUID)

    series_one_uid = str(series_one_instances[0].SeriesInstanceUID)
    series_two_uid = str(series_two_instances[0].SeriesInstanceUID)

    series_one_instances_uids = [str(i.SOPInstanceUID) for i in series_one_instances]
    series_two_instances_uids = [str(i.SOPInstanceUID) for i in series_two_instances]

    series_one_points = mock_up_inference_annotation(series_one_instances, radius_factor=0.1)
    series_two_points = mock_up_inference_annotation(series_two_instances, radius_factor=0.2)

    study_metadata = [
        {
            "dataType": "text",
            "value": f"{(len(series_one_instances) / len(series_two_instances)):.1f}x as much in first as in second "
            f"series ",
            "title": "Study metadata",
            "description": "Here you may put the description of the metadata for a study",
        }
    ]

    series_one_metadata = [
        {
            "dataType": "text",
            "value": f"{len(series_one_instances)} instances in {SERIES_ONE_KEY}",
            "title": "Series metadata",
            "description": "Here you may put the description of the metadata for a study",
        }
    ]

    series_two_metadata = [
        {
            "dataType": "text",
            "value": f"{len(series_two_instances)} instances in {SERIES_TWO_KEY}",
            "title": "Series metadata",
            "description": "Here you may put the description of the metadata for a study",
        }
    ]

    return generate_json_response(
        study_uid,
        study_metadata,
        series_one_uid,
        series_two_uid,
        series_one_instances_uids,
        series_two_instances_uids,
        series_one_points,
        series_two_points,
        series_one_metadata,
        series_two_metadata,
        series_one_class_name="Series-One-Mask",
        series_two_class_name="Series-Two-Mask",
    )


def generate_json_response(
    study_uid: str,
    study_metadata: List[Dict[str, Any]],
    series_one_uid: str,
    series_two_uid: str,
    series_one_instances_uids: List[str],
    series_two_instances_uids: List[str],
    series_one_points: List,
    series_two_points: List,
    series_one_metadata: List[Dict[str, Any]],
    series_two_metadata: List[Dict[str, Any]],
    series_one_class_name="Series-One-Mask",
    series_two_class_name="Series-Two-Mask",
    series_one_color="lightskyblue",
    series_two_color="lightskyblue",
    series_one_class_color="lightskyblue",
    series_two_class_color="lightskyblue",
    series_one_active_color="aquamarine",
    series_two_active_color="aquamarine",
) -> bytes:

    series_one_instances_dict = {}
    series_two_instances_dict = {}

    for idx, i_uid in enumerate(series_one_instances_uids):
        single_mask = {
            "points": series_one_points[idx],
            "color": series_one_color,
            "classColor": series_one_class_color,
            "activeColor": series_one_active_color,
            "className": series_one_class_name,
        }
        segments = [single_mask]
        series_one_instances_dict[i_uid] = {"rois": segments}

    series_one_instances_dict["metadata"] = series_one_metadata

    # for idx, i_uid in enumerate(series_two_instances_uids):
    #     single_mask = {
    #         "points": series_two_masks[idx].tolist(),
    #         "color": series_two_color,
    #         "classColor": series_two_class_color,
    #         "activeColor": series_two_active_color,
    #         "className": series_two_class_name,
    #     }
    #     segments = [single_mask]
    #     series_two_instances_dict[i_uid] = {"segments": segments}

    series_two_instances_dict["metadata"] = series_two_metadata

    study_dict = {
        study_uid: {
            "metadata": study_metadata,
            series_one_uid: series_one_instances_dict,
            series_two_uid: series_two_instances_dict,
        }
    }
    return orjson.dumps(study_dict)
