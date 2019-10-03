#!/bin/bash
set -o errexit -o pipefail

test_is_subdir() {
  local parent_dir=$(realpath "$1")
  local target_dir=$(realpath "$2")
  len1=$(echo $parent_dir | wc -c)
  if [[ "${target_dir:0:$len1}" != ${parent_dir}/ ]]; then
    echo "Bad parent dir: $2 is not under $1"
    exit 1
  fi
}

test_var_set() {
  local varname=$1

  if [[ -z "${!varname}" ]]; then
    echo "error: ${varname} is not set"
    exit 1
  fi
}

test_var_set XPI_SOURCE_REPO
test_var_set XPI_ARTIFACTS
test_var_set ARTIFACT_PREFIX

ARTIFACT_DIR=/builds/worker/artifacts
SOURCE_DIR=/builds/worker/checkouts/xpi-source
ARTIFACT_PREFIX_DIR="${ARTIFACT_DIR}/${ARTIFACT_PREFIX}"
mkdir -p "${ARTIFACT_PREFIX_DIR}"
test_is_subdir "${ARTIFACT_DIR}" "${ARTIFACT_PREFIX_DIR}"

# TODO set XPI_SOURCE_SECRET_NAME in private repos
if [[ -z "${!XPI_SOURCE_SECRET_NAME}" ]]; then
  cd /builds/worker/checkouts
  git clone "${XPI_SOURCE_REPO}" xpi-source
else
  # TODO private repo clone
  echo "Private repos aren't supported yet!"
  exit 1
fi

cd "${SOURCE_DIR}"
if [[ -z "${XPI_SOURCE_DIR}" ]]; then
  test_is_subdir "${SOURCE_DIR}" "${XPI_SOURCE_DIR}"
  cd "${XPI_SOURCE_DIR}"
fi

if [[ "${XPI_INSTALL_TYPE:-yarn}" == "yarn" ]]; then
  yarn install --frozen-lockfile
else
  npm install
fi

yarn build

# create manifest
# copy artifacts
