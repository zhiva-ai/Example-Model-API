from fastapi import FastAPI
import uvicorn
from starlette.responses import RedirectResponse

from app.endpoints import (
    single_series_endpoint,
    whole_study_endpoint,
    multiple_series_endpoint,
    multiple_series_annotation_endpoint
)

import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"


def create_app():
    app = FastAPI()

    app.include_router(
        single_series_endpoint.router,
        tags=["P"],
        responses={404: {"description": "Not found"}},
    )

    app.include_router(
        whole_study_endpoint.router,
        tags=["P"],
        responses={404: {"description": "Not found"}},
    )

    app.include_router(
        multiple_series_endpoint.router,
        tags=["P"],
        responses={404: {"description": "Not found"}},
    )

    app.include_router(
        multiple_series_annotation_endpoint.router,
        tags=["P"],
        responses={404: {"description": "Not found"}},
    )

    return app


app = create_app()


@app.get("/")
async def main():
    url = "/docs"
    response = RedirectResponse(url=url)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8011)
