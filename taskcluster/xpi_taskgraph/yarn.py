# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function, unicode_literals

import json
import subprocess


def _extract_content_from_command_output(output, prefix):
    prefixed_line = [line for line in output.split("\n") if line.startswith(prefix)][0]
    return json.loads(prefixed_line[len(prefix) :])
