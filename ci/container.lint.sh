#!/bin/bash

set -eux

cd "$(dirname "$0")"/..

pipenv sync --dev
pipenv run flake8
