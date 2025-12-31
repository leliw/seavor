#!/bin/bash

source ./config.sh

docker build \
--tag $DOCKER_REGISTRY/$IMAGE_NAME:latest .
# --progress=plain \

echo "Pushing ..."

docker push $DOCKER_REGISTRY/$IMAGE_NAME:latest
docker tag $DOCKER_REGISTRY/$IMAGE_NAME:latest $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION
docker push $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION