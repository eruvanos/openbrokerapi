# Development commands and notes




## Build pipeline

The project is checked and build with [Travis](https://travis-ci.com/eruvanos/openbrokerapi).

To publish a release use bumpversion. This will update the `setup.py` and tag the commit.
Travis will then push the new release to [PyPi](https://pypi.python.org/pypi/openbrokerapi).

```bash
bumpversion patch|minor
``` 


## Manual steps

### Test
```
./setup.py test
```

### Build
```
./setup.py sdist bdist_wheel
```

### Upload
```
twine upload -r testpypi dist/*
twine upload dist/*
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