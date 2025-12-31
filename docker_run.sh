#!/bin/bash

source ./config.sh

mkdir -p ./backend/data

docker run --rm \
-p 8080:8080 \
--env-file ./backend/.env \
--user $(id -u):$(id -g) \
--env UV_CACHE_DIR=/tmp/.cache/uv \
--mount type=bind,source=./backend/data,target=/data \
--name $SERVICE_NAME \
$DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION