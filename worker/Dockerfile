# FROM python:3.9

# WORKDIR /code
# RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
# COPY ./requirements.txt /code/requirements.txt
# RUN pip install --no-cache-dir --upgrade --no-install-recommends -r /code/requirements.txt
# COPY ./requirements_fast.txt /code/requirements_fast.txt
# RUN pip install --no-cache-dir --upgrade --no-install-recommends -r /code/requirements_fast.txt

# COPY . /code/

# CMD ["python", "-u", "-m", "worker.worker"]

# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get -qq update \
    && apt-get install -qq -y \
    git ffmpeg libsm6 libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements_torch.txt,target=requirements_torch.txt \
    python -m pip install -r requirements_torch.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Run the application.
CMD python -u -m worker.main
