# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from os.path import basename

from taskgraph.task import Task
from taskgraph.transforms.base import TransformSequence
from taskgraph.util.schema import resolve_keyed_by
from voluptuous import Required, Schema
from xpi_taskgraph.xpi_manifest import get_manifest

transforms = TransformSequence()
schema = Schema(
    {
        Required("primary-dependency"): Task,
        Required("worker-type"): str,
        Required("attributes"): dict,
        Required("run-on-tasks-for"): [str],
        Required("balrog"): dict
    },
)
transforms = TransformSequence()
transforms.add_validate(schema)


@transforms.add
def add_balrog_worker_config(config, tasks):
    if (
        config.params.get("version")
        and config.params.get("xpi_name")
        and config.params.get("head_ref")
        and config.params.get("moz_build_date")
    ):
        manifest = get_manifest()
        xpi_name = config.params["xpi_name"]
        xpi_manifest = manifest[xpi_name]
        xpi_addon_type = xpi_manifest["addon-type"]
        if xpi_addon_type == "system":
            xpi_version = config.params["version"]
            task_label = f"balrog-{xpi_name}"
            task_description = (
                "Creates a Balrog release for the signed {xpi_name}"
                " XPI package uploaded to https://ftp.mozilla.org/"
            ).format(xpi_name=xpi_name)
            for task in tasks:
                dep = task["primary-dependency"]
                worker = {
                    "action": "make-release",
                    "server": task["balrog"]["server"],
                    "channel": task["balrog"]["channel"],
                }
                task = {
                    "label": task_label,
                    "name": task_label,
                    "description": task_description,
                    "dependencies": {"release-signing": dep.label},
                    "worker-type": task["worker-type"],
                    "worker": worker,
                    "attributes": task["attributes"],
                    "run-on-tasks-for": task["run-on-tasks-for"],
                }
                yield task
