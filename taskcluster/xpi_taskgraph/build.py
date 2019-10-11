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
            env = task.setdefault("worker", {}).setdefault("env", {})
            env["XPI_REPOSITORY_TYPE"] = "git"
#            env["XPI_BASE_REPOSITORY"] = xpi_config["repo"]
#            env["XPI_HEAD_REPOSITORY"] = xpi_config["repo"]
            # TODO - check out in run-task, by overriding the repository config
            env["XPI_SOURCE_REPO"] = xpi_config["repo"]
            # TODO - allow for specifying the revision
            env["XPI_SOURCE_REVISION"] = "master"
#            env["XPI_HEAD_REV"] = "master"
#            env["XPI_HEAD_REF"] = "master"
            task["label"] = "build-{}".format(xpi_config["name"])
            task["treeherder"]["symbol"] = "B({})".format(
                xpi_config.get("treeherder-symbol", xpi_config["name"])
            )
            env["XPI_NAME"] = xpi_config["name"]
            task.setdefault("extra", {})["xpi-name"] = xpi_config["name"]
            env["XPI_TYPE"] = xpi_config["addon-type"]
            if xpi_config.get("directory"):
                env["XPI_SOURCE_DIR"] = xpi_config["directory"]
            if xpi_config.get("private-repo"):
                task.setdefault("scopes", []).append(
                    "secrets:get:{}".format(
                        config.graph_config["github_clone_secret"],
                    )
                )
                env["XPI_SSH_SECRET_NAME"] = config.graph_config["github_clone_secret"]
                # TODO xpi/* getArtifact scopes
                artifact_prefix = "xpi/build"
            else:
                artifact_prefix = "public/build"
            env["ARTIFACT_PREFIX"] = artifact_prefix
            if xpi_config.get("install-type"):
                env["XPI_INSTALL_TYPE"] = xpi_config["install-type"]
            task.setdefault("attributes", {})["addon-type"] = xpi_config["addon-type"]
            task.setdefault("attributes", {})["xpis"] = {}
            artifacts = task.setdefault("worker", {}).setdefault("artifacts", [])
            for artifact in xpi_config["artifacts"]:
                artifact_name = "{}/{}".format(
                    artifact_prefix, os.path.basename(artifact)
                )
                artifacts.append({
                    "type": "directory",
                    "name": artifact_prefix,
                    "path": "/builds/worker/artifacts",
                })
                task["attributes"]["xpis"][artifact] = artifact_name
            env["XPI_ARTIFACTS"] = ";".join(xpi_config["artifacts"])

            yield task
