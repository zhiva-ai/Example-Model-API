FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 iputils-ping  -y

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./app ./app

EXPOSE 8011
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8011"]
