# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function, unicode_literals

from taskgraph.target_tasks import _target_task as target_task


@target_task("release-build")
def target_tasks_release_build(full_task_graph, parameters, graph_config):
    """Select the set of tasks required for a release build."""

    def filter(task, parameters):
        # TODO phase
        return task.attributes.get("release", False)

    return [l for l, t in full_task_graph.tasks.iteritems() if filter(t, parameters)]
