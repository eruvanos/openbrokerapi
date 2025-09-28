#! /bin/bash
set -ex

args=""
if [[ $# == 0 ]]; then
    args="patch"
else
    args=$*
fi

echo "Pull changes"
git pull -r

echo "Run tests"
uv run pytest .

echo "Ruff"
uv run ruff check .

echo "Bump version"

#Bump version and create tag
bumpversion --commit $args

echo "Update lockfile"
uv lock
git add uv.lock
git commit --amend --no-edit

# create tag with version from .bumpversion.cfg
git tag -a "v$(uv version --short)" -m "v$(uv version --short)"

echo "Push to git"
git push --tag
