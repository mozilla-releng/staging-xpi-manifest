# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Apply some defaults and minor modifications to the jobs defined in the build
kind.
"""

from __future__ import absolute_import, print_function, unicode_literals
from copy import deepcopy
import json
import os

from taskgraph.transforms.base import TransformSequence
from xpi_taskgraph.xpi_manifest import get_manifest


transforms = TransformSequence()


@transforms.add
def test_tasks_from_manifest(config, tasks):
    manifest = get_manifest()
    for task in tasks:
        dep = task["primary-dependency"]
        task["attributes"] = dep.attributes.copy()
        del(task["primary-dependency"])
        task["dependencies"] = {"build": dep.label}
        xpi_name = dep.task["extra"]["xpi-name"]
        task.setdefault("extra", {})["xpi-name"] = xpi_name
        for xpi_config in manifest.get("xpis", []):
            if not xpi_config.get("active"):
                continue
            if xpi_config["name"] == xpi_name:
                break
        else:
            raise Exception("Can't determine the upstream xpi_config for {}!".format(xpi_name))
        env = task.setdefault("worker", {}).setdefault("env", {})
        for k, v in dep.task["payload"]["env"].items():
            if k.startswith("XPI_"):
                env[k] = v
        task["label"] = "test-{}".format(xpi_name)
        task["treeherder"]["symbol"] = "T({})".format(
            xpi_config.get("treeherder-symbol", xpi_config["name"])
        )
        if xpi_config.get("private-repo"):
            task.setdefault("scopes", []).append(
                "secrets:get:{}".format(
                    config.graph_config["github_clone_secret"]
                )
            )
            env["XPI_SSH_SECRET_NAME"] = config.graph_config["github_clone_secret"]
            # TODO xpi/* getArtifact scopes
            artifact_prefix = "xpi/build"
            # TODO put this in decision task?
            os.environ["TASKCLUSTER_PROXY_URL"] = "http://taskcluster"
            task["worker"]["taskcluster-proxy"] = True
        else:
            artifact_prefix = "public/build"
            env["ARTIFACT_PREFIX"] = artifact_prefix

        paths = []
        for artifact in xpi_config["artifacts"]:
            artifact_name = "{}/{}".format(
                artifact_prefix, os.path.basename(artifact)
            )
            paths.append(artifact_name)
        upstreamArtifacts = [
            {"taskId": "<build>", "paths": paths},
        ]
        env["XPI_UPSTREAM_URLS"] = json.dumps(upstreamArtifacts)

        yield task
