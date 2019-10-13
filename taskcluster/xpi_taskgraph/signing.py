# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Apply some defaults and minor modifications to the jobs defined in the build
kind.
"""

from __future__ import absolute_import, print_function, unicode_literals

from taskgraph.transforms.base import TransformSequence
from taskgraph.util.treeherder import inherit_treeherder_from_dep, replace_group
from taskgraph.util.schema import resolve_keyed_by


transforms = TransformSequence()


@transforms.add
def define_signing_flags(config, tasks):
    for task in tasks:
        dep = task["primary-dependency"]
        # Current kind will be prepended later in the transform chain.
        task["name"] = _get_dependent_job_name_without_its_kind(dep)
        task["attributes"] = dep.attributes.copy()
        task["attributes"]["signed"] = True
        if "run_on_tasks_for" in task["attributes"]:
            task.setdefault("run-on-tasks-for", task["attributes"]["run_on_tasks_for"])

        for key in ("worker-type", "worker.signing-type"):
            resolve_keyed_by(
                task,
                key,
                item_name=task["name"],
                level=config.params["level"],
            )
        group_symbol = task["treeherder"]["groupSymbol"]
        task["treeherder"] = inherit_treeherder_from_dep(task, dep)
        task["treeherder"]["symbol"] = replace_group(
            dep.task["extra"]["treeherder"]["symbol"], group_symbol
        )
        if "groupSymbol" in task["treeherder"]:
            del task["treeherder"]["groupSymbol"]
        yield task


@transforms.add
def build_signing_task(config, tasks):
    for task in tasks:
        dep = task["primary-dependency"]
        task["dependencies"] = {"build": dep.label}
        paths = [p for p in dep.attributes["xpis"].values() if p.endswith(".xpi")]
        if not paths:
            continue
        task["worker"]["upstream-artifacts"] = [
            {
                "taskId": {"task-reference": "<build>"},
                "taskType": "build",
                "paths": paths,
                # TODO change depending on type of xpi
                "formats": ["autograph_langpack"],
            }
        ]
        task.setdefault("extra", {})["xpi-name"] = dep.task["extra"]["xpi-name"]
        del task["primary-dependency"]
        yield task


def _get_dependent_job_name_without_its_kind(dependent_job):
    return dependent_job.label[len(dependent_job.kind) + 1:]
