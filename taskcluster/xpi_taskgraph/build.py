# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Apply some defaults and minor modifications to the jobs defined in the build
kind.
"""

from __future__ import absolute_import, print_function, unicode_literals

from taskgraph.transforms.base import TransformSequence


transforms = TransformSequence()


@transforms.add
def add_artifacts(config, tasks):
    for task in tasks:
        variant = task["attributes"]["build-type"]
        variant_config = {"xpis": []}  # TODO
        artifacts = task.setdefault("worker", {}).setdefault("artifacts", [])
        task["attributes"]["xpis"] = xpis = {}
        if "xpi-artifact-template" in task:
            artifact_template = task.pop("xpi-artifact-template")
            for xpi in variant_config["xpis"]:
                xpi_name = artifact_template["name"].format(
                    variant=variant, **xpi
                )
                artifacts.append(
                    {
                        "type": artifact_template["type"],
                        "name": xpi_name,
                        "path": artifact_template["path"].format(
                            variant=variant, **xpi
                        ),
                    }
                )

        yield task
