#!/bin/bash

set -eux

cd "$(dirname "$0")"

docker-compose down
