# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Apply some defaults and minor modifications to the jobs defined in the build
kind.
"""

from __future__ import absolute_import, print_function, unicode_literals
from copy import deepcopy
import os

from taskgraph.transforms.base import TransformSequence
from xpi_taskgraph.xpi_manifest import get_manifest


transforms = TransformSequence()


@transforms.add
def tasks_from_manifest(config, jobs):
    manifest = get_manifest()
    for job in jobs:
        for xpi_config in manifest.get("xpis", []):
            if not xpi_config.get("active"):
                continue
            task = deepcopy(job)
            task.setdefault("env", {})
            task["env"]["XPI_SOURCE_REPO"] = xpi_config["repo"]
            task["label"] = "build-{}".format(xpi_config["name"])
            task["env"]["XPI_NAME"] = xpi_config["repo"]
            task["env"]["XPI_TYPE"] = xpi_config["addon-type"]
            if xpi_config.get("directory"):
                task["env"]["XPI_SOURCE_DIR"] = xpi_config["directory"]
            if xpi_config.get("private-repo"):
                task["secrets"] = [config["github_clone_secret"]]
                task["env"]["XPI_SOURCE_SECRET_NAME"] = config["github_clone_secret"]
                # TODO xpi/* getArtifact scopes
                artifact_prefix = "xpi/build"
            else:
                artifact_prefix = "public/build"
            task["env"]["ARTIFACT_PREFIX"] = artifact_prefix
            if xpi_config.get("install-type"):
                task["env"]["XPI_INSTALL_TYPE"] = xpi_config["install-type"]
            task.setdefault("attributes", {})["addon-type"] = xpi_config["addon-type"]
            artifacts = task.setdefault("worker", {}).setdefault("artifacts", [])
            for artifact in xpi_config["artifacts"]:
                artifact_name = os.path.basename(artifact),
                artifacts.append({
                    "type": "file",
                    "name": "{}/{}".format(artifact_prefix, artifact_name),
                    "path": artifact,
                })
            task["env"]["XPI_ARTIFACTS"] = ";".join(xpi_config["artifacts"])

            yield task
