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
from taskgraph.util.taskcluster import get_artifact_url
from xpi_taskgraph.xpi_manifest import get_manifest


transforms = TransformSequence()


@transforms.add
def test_tasks_from_manifest(config, tasks):
    manifest = get_manifest()
    for task in tasks:
        dep = task["primary-dependency"]
        task["attributes"] = dep.attributes.copy()
        del(task["primary-dependency"])
        xpi_name = dep.task["extra"]["xpi-name"]
        task.setdefault("extra", {})["xpi-name"] = xpi_name
        # TODO find the xpi_config
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
            task["secrets"] = [config["github_clone_secret"]]
            # TODO xpi/* getArtifact scopes
            artifact_prefix = "xpi/build"
        else:
            artifact_prefix = "public/build"
            task["worker"]["env"]["ARTIFACT_PREFIX"] = artifact_prefix

        upstream_artifact_urls = []
        for artifact in xpi_config["artifacts"]:
            artifact_name = "{}/{}".format(
                artifact_prefix, os.path.basename(artifact)
            )
            upstream_artifact_urls.append(
                get_artifact_url('<{}>'.format(dep.label), artifact_name)
            )

        task["worker"]["env"]["XPI_UPSTREAM_URLS"] = "|".join(xpi_config["artifacts"])

        yield task
