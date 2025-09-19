#!/bin/bash
set -e

docker build -t pydantic-generator .
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/usr/src/app" pydantic-generator