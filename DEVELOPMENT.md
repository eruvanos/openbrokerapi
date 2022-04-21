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

### Test
```
poetry run pytest .
```

### Build
```
poetry build
```

### Upload
```
# Test PyPI
poetry publish --build -r testpypi
# PyPI
poetry publish --build
```

### Install from testpypi
```
pip install -i https://testpypi.python.org/simple openbrokerapi
```

### Create docs

```
cd doc
sphinx-build -b html . _build
```