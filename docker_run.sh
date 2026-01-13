#!/bin/bash

source ./config.sh


docker run --rm \
-p 8080:8080 \
--name seavor \
$DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_VERSION