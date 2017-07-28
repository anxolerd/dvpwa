#!/bin/bash
set -e

docker-compose down
docker volume ls -qf dangling=true | xargs -r docker volume rm
docker-compose build
