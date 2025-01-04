#!/bin/bash

# docker_run.sh
# Script to run the Docker container for the Pygame project

# Define the Docker image name
IMAGE_NAME="pygame-app"

# Allow Docker to access the X server (Linux only)
# Uncomment the following line if you're on Linux
# xhost +local:docker

# Run the Docker container
docker run -it \
    --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    $IMAGE_NAME

# Revoke Docker's access to the X server (Linux only)
# Uncomment the following line if you're on Linux
# xhost -local:docker
