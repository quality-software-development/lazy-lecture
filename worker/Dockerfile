FROM python:3.9

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /code
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./requirements_fast.txt /code/requirements_fast.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements_fast.txt

COPY . /code/
