#!/bin/bash
set -o errexit -o pipefail

export XPI_SOURCE_REPO=https://github.com/mozilla/shield-studies-addon-utils
export XPI_NAME=shield-study-helper-addon
export XPI_TYPE=standard
export XPI_SOURCE_DIR=misc/shield-study-helper-addon
export ARTIFACT_PREFIX=public/build
export XPI_INSTALL_TYPE=npm
export XPI_ARTIFACTS=linked-addon.xpi

python3 build.py
