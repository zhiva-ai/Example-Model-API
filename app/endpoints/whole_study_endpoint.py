import orjson
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from app.docker_logs import get_logger
from typing import List, Dict, Any
import io
import pydicom
from pydicom.dataset import FileDataset
import json

router = APIRouter(prefix="/whole-study-endpoint")

logger = get_logger("whole-study-endpoint-logger")


@router.post("/predict", response_class=ORJSONResponse)
async def predict(items: List[str]):
    """
    :param items:
    :return: json in the specified format
    """

    instances = [
        pydicom.dcmread(io.BytesIO(bytes(json.loads(instance)))) for instance in items
    ]

    study_instance_uid = str(instances[0].StudyInstanceUID)

    series_dict = get_instances_for_each_series(instances)
    series_uids = list(map(lambda uid: str(uid), series_dict.keys()))

    logger.info(f"{len(series_uids)} series in the study")

    series_metadata = [
        {
            "metadata": [
                {
                    "dataType": "text",
                    "value": f"Instances in series: {len(series_dict[uid])}",
                    "title": "Series metadata",
                }
            ]
        }
        for uid in series_dict.keys()
    ]

    study_metadata = [
        {
            "dataType": "text",
            "value": f"{len(series_uids)} series in the study",
            "title": "Study metadata",
            "description": "Here you may put the description of the metadata for a study",
        }
    ]

    return generate_json_response(
        study_instance_uid, series_uids, study_metadata, series_metadata
    )


def generate_json_response(
    study_instance_uid: str,
    series_uids: List[str],
    study_metadata: List[Dict[str, Any]],
    series_metadata: List[List[Dict[str, Any]]],
) -> bytes:

    series_dict = {
        s_uid: s_metadata for s_uid, s_metadata in zip(series_uids, series_metadata)
    }
    series_dict["metadata"] = study_metadata

    study_dict = {study_instance_uid: series_dict}

    return orjson.dumps(study_dict)


def get_instances_for_each_series(
    instances: List[FileDataset],
) -> Dict["str", List[FileDataset]]:
    series_uids = set([i.SeriesInstanceUID for i in instances])

    series_dict = {}
    for s_uid in series_uids:
        series_dict[s_uid] = list(
            filter(lambda i: i.SeriesInstanceUID == s_uid, instances)
        )

    for s_uid in series_uids:
        series_dict[s_uid].sort(key=lambda i: i.InstanceNumber)

    return series_dict
