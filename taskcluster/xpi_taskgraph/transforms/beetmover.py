# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from taskgraph.task import Task
from taskgraph.transforms.base import TransformSequence
from voluptuous import Required, Schema
from xpi_taskgraph.xpi_manifest import get_manifest

transforms = TransformSequence()
schema = Schema(
    {
        Required("primary-dependency"): Task,
        Required("worker-type"): str,
        Required("attributes"): dict,
        Required("run-on-tasks-for"): [str],
        Required("bucket-scope"): str,
    }
)
transforms = TransformSequence()
transforms.add_validate(schema)


@transforms.add
def add_beetmover_worker_config(config, tasks):
    manifest = get_manifest()
    xpi_name = config.params["xpi_name"]
    xpi_manifest = manifest[xpi_name]
    xpi_addon_type = xpi_manifest["addon-type"]
    if xpi_addon_type == "system":
        xpi_version = config.params.get("version")
        xpi_destination = (
            "pub/system-addons/{xpi_name}/"
            "{xpi_name}@mozilla.org-{xpi_version}-signed.xpi"
        ).format(xpi_name=xpi_name, xpi_version=xpi_version)
        xpi_destinations = [xpi_destination]
        task_label = f"beetmover-{xpi_name}"
        task_description = (
            "Uploads the signed {xpi_name} XPI package to "
            "https://ftp.mozilla.org/{xpi_destination}"
        ).format(xpi_name=xpi_name, xpi_destination=xpi_destination)
        for task in tasks:
            dep = task["primary-dependency"]
            task_ref = {"task-reference": "<release-signing>"}
            paths = list(dep.attributes["xpis"].values())
            artifact_map_paths = {
                path: {"destinations": xpi_destinations} for path in paths
            }
            task = {
                "label": task_label,
                "name": task_label,
                "description": task_description,
                "dependencies": {"release-signing": dep.label},
                "worker-type": task["worker-type"],
                "worker": {
                    "upstream-artifacts": [
                        {
                            "taskId": task_ref,
                            "taskType": "signing",
                            "paths": paths,
                        },
                    ],
                    "action": "direct-push-to-bucket",
                    "version": xpi_version,
                    "bucket": "net-mozaws-stage-delivery-archive",
                    "app-name": xpi_name,
                    "artifact-map": [
                        {
                            "taskId": task_ref,
                            "paths": artifact_map_paths,
                        }
                    ],
                },
                "scopes": [
                    task["bucket-scope"],
                    "project:xpi:beetmover:action:direct-push-to-bucket",
                ],
                "attributes": task["attributes"],
                "run-on-tasks-for": task["run-on-tasks-for"],
            }
            yield task
