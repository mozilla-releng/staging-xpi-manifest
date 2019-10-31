# Adding a new xpi

## Creating the repo

During this testing phase, the test template source repo is https://github.com/escapewindow/test-xpi-public . At some point we'll move this to a permanent location and set this up as a github template repo.

The files we need are:

    .cron.yml
    .taskcluster.yml
    CODE_OF_CONDUCT.md
    LICENSE
    taskcluster/*

though other files may be helpful as well, e.g. `README.md`, `.gitignore`, `eslintrc.js`.

## Enabling taskcluster CI automation

We currently require a patch like [this](https://hg.mozilla.org/ci/ci-configuration/rev/b3ddb3eca07cd6864bc5fe8dcc46980c5420662a) to enable taskcluster CI automation for on-push and pull request in this repo.

We use [phabricator](https://moz-conduit.readthedocs.io/en/latest/phabricator-user.html#) to submit patches for review.

Ideally we can add some sort of regex or wildcard for all future repos underneath the new github organization, and avoid having to write a ci-configuration patch per new repo.

## Using taskcluster CI automation

Once Taskcluster CI automation is enabled, we'll generate a decision task and task graph on push or PR. This dynamically adds tasks using the following logic:

  - Find all `package.json` files in the repository. The directory that `package.json` lives in is the package directory.

    - Either find `yarn.lock` or `package-lock.json` in the directory. This determines whether the task will install dependencies via `yarn install --frozen-lockfile` or `npm install`.

    - Create a build task per package directory. These will only be scheduled when `.taskcluster.yml`, a file under `taskcluster/`, or a file under the package directory have been changed since the previous build.

    - The package directories must have unique names per repository. So a layout like

    ```
    ./xpis/one/package.json
    ./xpis/two/package.json
    ./three/package.json
    ./package.json
    ```

    works, while a layout like

    ```
    xpis/one/package.json
    more-xpis/one/package.json
    ```

    doesn't (duplicate `one` package directory names). A package directory at the root of the repository will be named `src`.

  - Read `package.json` and create a test task per entry in `scripts` that starts with either `test` or `lint`. (These test names must be either alphanumeric, or only include the special characters `:_-`).

    - The `test` script will be run in release build graphs. All test or lint scripts will be run on push or PR.

    - Similar to the builds, these tests will only be scheduled when `.taskcluster.yml`, a file under `taskcluster/`, or a file under the package directory have been changed since the previous test run.


