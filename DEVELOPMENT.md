# Development commands and notes

## Contributing

Use ruff to format your code (`uv run ruff format .`)!

## Build pipeline

To publish a release use bumpversion. This will update the `pyproject.toml` and tag the commit.
The `python-publish.yml` GitHub Action picks up the new tag, builds with `uv build` and publishes to Test-PyPI and PyPI with `uv publish` via trusted publishing.

> To trigger the whole build process use `ship.sh`.

```bash
./ship.sh patch|minor
```


## Manual steps

### Install dependencies
```
uv sync --extra dev
```

### Test
```
uv run pytest .
```

### Build
```
uv build
```

### Upload
```
# Test PyPI
uv publish --publish-url https://test.pypi.org/legacy/
# PyPI
uv publish
```

### Install from testpypi
```
pip install -i https://testpypi.python.org/simple openbrokerapi
```

### Create docs

```
cd doc
uv run sphinx-build -b html . _build
```
