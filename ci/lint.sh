#!/bin/bash

set -eux

cd "$(dirname "$0")"

docker-compose build
docker-compose run -u"$(id -u)":"$(id -g)" app ./ci/container.lint.sh
