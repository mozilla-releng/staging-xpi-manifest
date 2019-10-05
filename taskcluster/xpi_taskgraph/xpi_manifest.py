# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function, unicode_literals

import json
import os
import time
from datetime import datetime

from taskgraph.util.schema import validate_schema
from taskgraph.util.vcs import calculate_head_rev, get_repo_path, get_repository_type
from taskgraph.util import yaml
from taskgraph.util.memoize import memoize
from taskgraph.util.readonlydict import ReadOnlyDict
from voluptuous import (
    ALLOW_EXTRA,
    Optional,
    Required,
    Schema,
    Any,
)

MANIFEST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "xpi-manifest.yml"
)


base_schema = Schema({
    Required('xpis'): [{
        Required('name'): basestring,
        Required('repo'): basestring,
        Optional('directory'): basestring,
        Optional('active'): bool,
        Required('artifacts'): [basestring],
        Required('addon-type'): Any('system', 'standard'),
        Optional('install-type'): Any('npm', 'yarn'),
        Optional('treeherder-symbol'): basestring,
    }],
})


@memoize
def get_manifest():
    manifest = ReadOnlyDict(yaml.load_yaml(MANIFEST_PATH))
    validate_schema(base_schema, manifest.copy(), 'Invalid manifest:')
    # any other checks?
    return manifest
