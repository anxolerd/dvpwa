#!/bin/bash
set -e

docker-compose down --volumes
docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1 --memory 512m

