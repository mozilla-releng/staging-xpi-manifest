# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import json
import sys
from os.path import basename
from pprint import pformat as pf

from taskgraph.transforms.base import TransformSequence

transforms = TransformSequence()


@transforms.add
def add_beetmover_config(config, tasks):
    for task in tasks:
        if (
            config.params.get("version")
            and config.params.get("xpi_name")
            and config.params.get("build_number")
        ):
            dependency = task.pop("primary-dependency")
            label = f"release-beetmover-{config.params.get('xpi_name')}"
            task["label"] = task["name"] = label
            task["description"] = (
                "Upload signed {xpi_name} XPI archive to "
                "https://ftp.mozilla.org/pub/system-addons/"
            ).format(xpi_name=config.params.get("xpi_name"))
            task["dependencies"] = {"release-signing": dependency.label}
            task["worker"]["upstream-artifacts"] = [
                {
                    "taskId": {"task-reference": "<release-signing>"},
                    "taskType": "signing",
                    "paths": list(dependency.attributes["xpis"].values()),
                    "locale": "multi",
                }
            ]
            task["worker"]["release-properties"] = {
                "app-name": config.params.get("xpi_name"),
                "app-version": config.params.get("version"),
                "branch": basename(config.params.get("head_ref")),
                "build-id": str(config.params.get("build_number")),
                "hash-type": "sha512",  # ?
                "platform": "gecko",  # ?
            }
            yield task
