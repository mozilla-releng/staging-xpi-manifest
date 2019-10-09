# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# %ARG           NODE_VERSION
FROM          node:$NODE_VERSION
MAINTAINER    Aki Sasaki <aki@mozilla.com>

RUN mkdir /builds && \
    mkdir -p /builds/worker/artifacts && \
    chown -R node:node /builds/worker

# %include-run-task

COPY build.py /usr/local/bin/build.py

RUN apt-get update && apt-get install -y --force-yes --no-install-recommends \
    mercurial

ENV SHELL=/bin/bash \
    HOME=/builds/worker \
    PATH=/builds/worker/.local/bin:$PATH

VOLUME /builds/worker/checkouts
VOLUME /builds/worker/.cache
USER node

# Set a default command useful for debugging
CMD ["/bin/bash", "--login"]
