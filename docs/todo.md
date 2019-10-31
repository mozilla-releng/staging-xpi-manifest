# To do

- We probably want to create a new Github organization for the xpi manifest repo and the source repos.

- We likely want to streamline adding a new repository, possibly by adding wildcard or regex support to [ci-configuration](https://hg.mozilla.org/ci/ci-configuration/) and [ci-admin](https://hg.mozilla.org/ci/ci-admin/).

- require a specific revision in release-promotion.py

- remove the `echo` from `yarn test`. I just added it because all my example repos had busted `yarn test`s.
