# Development commands and notes

## Contributing

Use black to format your code!

## Build pipeline

To publish a release use bumpversion. This will update the `pyproject.toml` and tag the commit.
#TODO a Github action will pick up the new tag and publish a new version on pypi

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
