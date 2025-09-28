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
bumpversion --tag --commit $args

#seperate commit with version in comment
#git commit -m "v$(cat .bumpversion.cfg|grep current_version|tr -d ' '|cut -f 2 -d '=')""

echo "Push to git"
git push --tag
